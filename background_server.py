"""Run in WSL; communicate with the removable Windows Ren'Py mod via files."""
import asyncio
import json
from pathlib import Path
import sys
import time
import uuid

from mcp.server.fastmcp import FastMCP, Image

directory = Path(sys.argv[1])
mcp = FastMCP("everlasting_summer_background")
lock = asyncio.Lock()
ACTIONS = {"screenshot", "advance", "up", "down", "left", "right", "select", "back"}


@mcp.tool()
async def game(action: str = "screenshot") -> Image:
    """Read or control the game without OS input. Actions: screenshot, advance,
    up/down/left/right (menu focus), select, back. Inspect every returned image.
    Never automatically retry timed-out actions: they may already have executed.
    """
    if action not in ACTIONS:
        raise ValueError("Unsupported action.")
    async with lock:
        if not directory.is_dir():
            raise RuntimeError("Start the game with codex_bridge.rpy installed first.")
        request = directory / "request.json"
        if request.exists():
            raise RuntimeError("An earlier request is pending. Do not queue another action.")
        identifier = uuid.uuid4().hex
        temporary = directory / (identifier + ".tmp")
        temporary.write_text(json.dumps({"id": identifier, "action": action}), encoding="utf-8")
        temporary.replace(request)
        response = directory / (identifier + ".json")
        image = directory / (identifier + ".png")
        deadline = time.monotonic() + 15
        while not response.exists():
            if time.monotonic() >= deadline:
                raise RuntimeError("Game did not respond within 15s. Action may have executed; "
                                   "do not repeat it. Restore the window and request a screenshot.")
            await asyncio.sleep(0.1)
        try:
            result = json.loads(response.read_text(encoding="utf-8"))
            if result.get("error"):
                raise RuntimeError(result["error"])
            return Image(data=image.read_bytes(), format="png")
        finally:
            response.unlink(missing_ok=True)
            image.unlink(missing_ok=True)


if __name__ == "__main__":
    mcp.run(transport="stdio")
