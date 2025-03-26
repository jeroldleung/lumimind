import asyncio

from dotenv import load_dotenv

from app.websocket_server import WebsocketServer

if __name__ == "__main__":
    load_dotenv()
    server = WebsocketServer()
    asyncio.run(server.start())
