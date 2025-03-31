import asyncio
import os
import signal

from loguru import logger
from websockets.asyncio.server import serve

from app.manager import Manager


class Server:
    def __init__(self):
        self.host = os.environ["SERVER_HOST"]
        self.port = os.environ["SERVER_PORT"]

    async def start(self):
        manager = Manager()
        async with serve(manager.handle, self.host, self.port) as server:
            logger.success("Server started")
            # Close the server when receiving SIGTERM and SIGINT.
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, server.close)
            loop.add_signal_handler(signal.SIGINT, server.close)
            await server.wait_closed()
            logger.success("Server closed")
