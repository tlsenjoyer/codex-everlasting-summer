import json
import os
from pathlib import Path
import sys
import tempfile
import textwrap
import types
from unittest.mock import Mock, patch

class StoreDict(dict):
    pass

source = Path(__file__).with_name('codex_bridge.rpy').read_text()
source = textwrap.dedent(source.split('init 999 python hide:\n')[1])
source = source.replace('from collections import Mapping', 'from collections.abc import Mapping')
engine = types.ModuleType('renpy')
engine.queue_event = Mock()
engine.screenshot_to_bytes = lambda size: b'png'
engine.exports = engine
with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, HOME=home), patch.dict(sys.modules, {'renpy':engine, 'renpy.exports':engine}):
    namespace = {'dict':StoreDict, 'basestring':str, 'config':types.SimpleNamespace(periodic_callbacks=[])}
    exec(compile(source,'bridge-test','exec'), namespace)
    directory=Path(namespace['directory'])
    for action in ('screenshot', 'advance', 'invalid'):
        identifier = {'screenshot':'a', 'advance':'b', 'invalid':'c'}[action]*32
        (directory/'request.json').write_text(json.dumps({'id':identifier,'action':action}))
        namespace['tick']()
        if namespace['pending'][0]:
            req,_ = namespace['pending'][0]
            namespace['pending'][0] = (req,0)
            namespace['tick']()
        result = json.loads((directory/(identifier+'.json')).read_text())
        assert (result['error'] is None) == (action != 'invalid')
    assert engine.queue_event.call_count == 2
    assert engine.queue_event.call_args_list[0].args == ('dismiss_unfocused',)
    assert engine.queue_event.call_args_list[1].kwargs == {'up':True}
print('Passed: JSON requests work with RenPy store.dict substitution; screenshots, events, and invalid-action refusal.')
