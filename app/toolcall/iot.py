from typing import Any, Dict

from websockets.asyncio.server import ServerConnection


class Device:
    def __init__(self, conn: ServerConnection):
        self.conn = conn
        self.tools = []

    def registry(self, msg: Dict[str, Any]):
        if "descriptors" in msg:
            self.tools.append(msg["descriptors"])

    def schema(self):
        pass

    def call(self, **args):
        pass
