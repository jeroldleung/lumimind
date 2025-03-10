import asyncio

from app import WebsocketServer

if __name__ == "__main__":
    server = WebsocketServer("0.0.0.0", 8000)
    asyncio.run(server.start())
