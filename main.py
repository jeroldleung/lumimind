import asyncio

from dotenv import load_dotenv
from websockets.asyncio.server import serve

from app.handler import handle_connection


async def main():
    async with serve(handle_connection, "0.0.0.0", 8000) as server:
        await server.serve_forever()


if __name__ == "__main__":
    assert load_dotenv(), "Failed to load .env file"
    asyncio.run(main())
