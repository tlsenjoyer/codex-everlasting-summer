# Everlasting Summer Codex bridge

A removable Ren'Py mod and a Python MCP server for reading and controlling
Everlasting Summer from Codex in WSL while the Windows game is minimized.
Requests and screenshots pass through a shared directory; no network port or
Windows keyboard automation is used.

## Install

1. Close the game. Copy `codex_bridge.rpy` into the Steam game's `game` directory,
   usually `C:\Program Files (x86)\Steam\steamapps\common\Everlasting Summer\game`.
   Keep the filename unchanged. No original game files need replacing.
2. In this repository in WSL, create the server environment:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

3. Start the game. The mod creates
   `C:\Users\YOUR_NAME\codex-everlasting-summer\bridge` under the Windows user's
   home directory. Use the corresponding WSL path below.
4. Register the server from this repository in WSL:

   ```bash
   codex mcp add everlasting_summer -- \
     "$PWD/.venv/bin/python" "$PWD/background_server.py" \
     /mnt/c/Users/YOUR_NAME/codex-everlasting-summer/bridge
   ```

   If an older server is registered under that name, first run
   `codex mcp remove everlasting_summer`. Start a new Codex session after registration.

## Use

The `game` tool accepts `screenshot` (default), `advance`, `up`, `down`, `left`,
`right`, `select`, and `back`. Directions move menu focus; `select` activates
the focused option; `back` opens the game menu. Each request returns a screenshot
after a short delay. Inspect each image before deciding the next action.

Start with a screenshot, then verify one advance and menu navigation. For
predictable reading, set text speed to maximum and disable auto-advance. Use a
separate save slot when experimenting: actions can change the story and menus
can overwrite saves. Run only one server against a bridge directory.

If a request times out, it may already have executed. Do not repeat the action;
restore the game window and request a screenshot. If `request.json` remains
pending, close the game and stop the server before removing that file, then
restart both and inspect a fresh screenshot. The bridge directory contains
screenshots and should remain private to your local user.

## Verification and limits

The source was recovered from the installed bridge used with Ren'Py
7.4.11.2266 (Python 2). The referenced play test verified fresh screenshots,
dialogue advance, menu navigation, and one story choice while Windows reported
the game minimized and inactive. A full playthrough and other engine versions
have not been verified. Screenshots depend on the engine's latest render.

Run the standalone regression check with Python 3:

```bash
python3 test_bridge.py
```

It mocks the engine and checks request handling, screenshot responses, invalid
actions, and key-down/key-up events, including Ren'Py's replacement `dict` type.
It does not launch the game or verify rendering.

## Remove

Close the game and remove both `game/codex_bridge.rpy` and
`game/codex_bridge.rpyc`. Unregister the server with
`codex mcp remove everlasting_summer`. The user-home bridge directory can then
be deleted. No game assets, saves, or generated screenshots are included here.
