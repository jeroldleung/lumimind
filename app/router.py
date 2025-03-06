from loguru import logger
from websockets.asyncio.server import ServerConnection


class Router:
    @staticmethod
    async def route(websocket: ServerConnection):
        if websocket.request.path == "/xiaozhi/v1":
            logger.info(f"Client({websocket.id}) connected")
            await websocket.send("Hello World")
        else:
            await websocket.send("Error: Bad Request")
            logger.info(f"Client({websocket.id}) disconnected")
