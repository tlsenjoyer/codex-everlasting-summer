# Remove this file and codex_bridge.rpyc to uninstall.
init 999 python hide:
    import os
    import json
    from collections import Mapping
    import time
    import re
    import renpy.exports as renpy

    directory = os.path.join(os.path.expanduser("~"), "codex-everlasting-summer", "bridge")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    pending = [None]
    allowed = ("screenshot", "advance", "up", "down", "left", "right", "select", "back")
    events = {"advance": "dismiss_unfocused", "up": "focus_up", "down": "focus_down",
              "left": "focus_left", "right": "focus_right", "select": "button_select",
              "back": "game_menu"}

    def respond(request, error=None):
        identifier = request["id"]
        try:
            if error is None:
                data = renpy.screenshot_to_bytes(None)
                if not data:
                    raise Exception("Renderer returned no screenshot.")
                with open(os.path.join(directory, identifier + ".png"), "wb") as stream:
                    stream.write(data)
        except Exception as exc:
            error = str(exc)
        result = {"id": identifier, "error": error}
        destination = os.path.join(directory, identifier + ".json")
        with open(destination + ".tmp", "w") as stream:
            json.dump(result, stream)
        os.rename(destination + ".tmp", destination)

    def tick():
        if pending[0] is not None:
            request, due = pending[0]
            if time.time() >= due:
                pending[0] = None
                respond(request)
            return
        path = os.path.join(directory, "request.json")
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r") as stream:
                request = json.load(stream)
        except (ValueError, IOError):
            os.remove(path)
            return
        os.remove(path)
        if not isinstance(request, Mapping):
            return
        identifier = request.get("id", "")
        if not isinstance(identifier, basestring) or not re.match(r"\A[0-9a-f]{32}\Z", identifier):
            return
        action = request.get("action")
        if action not in allowed:
            respond(request, "Unsupported action.")
            return
        try:
            if action != "screenshot":
                event = events[action]
                renpy.queue_event(event)
                renpy.queue_event(event, up=True)
            pending[0] = (request, time.time() + 0.7)
        except Exception as exc:
            respond(request, str(exc))

    # shortcut: screenshots use the last engine render; verify freshness when minimized.
    config.periodic_callbacks.append(tick)
