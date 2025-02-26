from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosedOK

from .schemas import MessageToClient, MessageType
from .utils import message_from_client, message_to_client


async def handle_text_message(websocket: ServerConnection, msg: str):
    logger.debug(f"Message from client {websocket.id}: {msg}")
    m = message_from_client(msg)
    # handle different type of messages
    if m.type == MessageType.HELLO:
        m_to_client = MessageToClient(type=MessageType.HELLO)
        await websocket.send(message_to_client(m_to_client))
        logger.info(f"Handshake with client: {websocket.id}")


async def handle_audio_message(websocket: ServerConnection, msg: bytes):
    pass


async def handle_connection(websocket: ServerConnection):
    logger.success(f"Client connected: {websocket.id}")

    while True:
        try:
            msg = await websocket.recv()
            if isinstance(msg, str):
                await handle_text_message(websocket, msg)
            elif isinstance(msg, bytes):
                await handle_audio_message(websocket, msg)
        except ConnectionClosedOK:
            break

    logger.success(f"Client disconnected: {websocket.id}")
