from websockets.asyncio.server import ServerConnection


class Router:
    @staticmethod
    async def route(websocket: ServerConnection):
        if websocket.request.path == "/xiaozhi/v1":
            await websocket.send("Hello World")
        else:
            await websocket.send("Error: Bad Request")
