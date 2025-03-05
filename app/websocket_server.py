from websockets.asyncio.server import serve

from .handler import handle_connection


class WebsocketServer:
    @staticmethod
    async def start():
        async with serve(handle_connection, "0.0.0.0", 8000) as server:
            await server.serve_forever()
