from dotenv import load_dotenv
from websockets.sync.server import serve

from app.handler import handle_connection


def main():
    with serve(handle_connection, "0.0.0.0", 8000) as server:
        server.serve_forever()


if __name__ == "__main__":
    assert load_dotenv(), "Failed to load .env file"
    main()
