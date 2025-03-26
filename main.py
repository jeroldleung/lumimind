import asyncio

from dotenv import load_dotenv

from app.server import Server

if __name__ == "__main__":
    load_dotenv()
    server = Server()
    asyncio.run(server.start())
