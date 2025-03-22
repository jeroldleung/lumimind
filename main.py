import asyncio

from app import WebsocketServer

if __name__ == "__main__":
    server = WebsocketServer()
    asyncio.run(server.start())
