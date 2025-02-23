from loguru import logger
from websockets.exceptions import ConnectionClosedOK
from websockets.sync.server import ServerConnection


def handle_text_message(websocket: ServerConnection, msg: str):
    pass


def handle_audio_message(websocket: ServerConnection, msg: bytes):
    pass


def handle_connection(websocket: ServerConnection):
    logger.success(f"Client connected: {websocket.id}")

    while True:
        try:
            msg = websocket.recv()
            if isinstance(msg, str):
                handle_text_message(websocket, msg)
            elif isinstance(msg, bytes):
                handle_audio_message(websocket, msg)
        except ConnectionClosedOK:
            break

    logger.success(f"Client disconnected: {websocket.id}")
