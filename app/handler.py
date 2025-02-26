import asyncio

from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosedOK

from .audio import wav_to_opus
from .llm import stream_llm_output
from .schemas import AudioState, MessageToClient, MessageType
from .utils import message_from_client, message_to_client


async def handshake(websocket: ServerConnection):
    m_to_client = MessageToClient(type=MessageType.HELLO)
    await websocket.send(message_to_client(m_to_client))


async def stream_audio_bytes(websocket: ServerConnection, user_input: str) -> str:
    # tell device that the audio is ready for playing
    tts_start = MessageToClient(type=MessageType.TTS, state=AudioState.START)
    await websocket.send(message_to_client(tts_start))

    # send audio bytes
    audio_stream, response_text = stream_llm_output(user_input), ""
    n_wait_ms = 0
    try:
        while True:
            audio_str = next(audio_stream)
            for opus_bytes in wav_to_opus(audio_str):
                n_wait_ms += 1
                await websocket.send(opus_bytes)
    except StopIteration as e:
        response_text = e.value

    # send audio text to client
    sentence_start = MessageToClient(
        type=MessageType.TTS,
        state=AudioState.SENTENCE_START,
        text=response_text,
    )
    await websocket.send(message_to_client(sentence_start))

    # wait for client to finish playing audio
    await asyncio.sleep(n_wait_ms * 60 / 1000)

    # tell device that the audio stream is stoped
    tts_stop = MessageToClient(type=MessageType.TTS, state=AudioState.STOP)
    await websocket.send(message_to_client(tts_stop))

    return response_text


async def handle_text_message(websocket: ServerConnection, msg: str):
    logger.debug(f"Message from client {websocket.id}: {msg}")
    m = message_from_client(msg)
    # handle different type of messages
    if m.type == MessageType.HELLO:
        await handshake(websocket)
        logger.info(f"Handshake with client: {websocket.id}")
    elif m.type == MessageType.LISTEN and m.state == AudioState.DETECT:
        response_text = await stream_audio_bytes(websocket, m.text)
        logger.info(f"Message to client {websocket.id}: {response_text}")


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
