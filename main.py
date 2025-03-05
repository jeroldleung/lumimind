import asyncio

from app import WebsocketServer

if __name__ == "__main__":
    asyncio.run(WebsocketServer.start())
