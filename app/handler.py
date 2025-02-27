import asyncio
import json

from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosedOK

from .audio import audio_to_text, opus_to_pcm, wav_to_opus
from .llm import stream_llm_output
from .schemas import AudioState, MessageToClient, MessageType
from .utils import message_from_client, message_to_client

user_audio_input = []


async def handshake(websocket: ServerConnection):
    m_to_client = MessageToClient(type=MessageType.HELLO)
    await websocket.send(message_to_client(m_to_client))
    logger.info(f"Handshake with client: {websocket.id}")
    # temporarily handle volume
    volume = {
        "type": "iot",
        "commands": [
            {"name": "Speaker", "method": "SetVolume", "parameters": {"volume": 75}}
        ],
    }
    await websocket.send(json.dumps(volume))


async def stream_audio_bytes(websocket: ServerConnection, user_input: str):
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
    logger.info(f"Message to client {websocket.id}: {response_text}")

    # wait for client to finish playing audio
    await asyncio.sleep(n_wait_ms * 60 / 1000)

    # tell device that the audio stream is stoped
    tts_stop = MessageToClient(type=MessageType.TTS, state=AudioState.STOP)
    await websocket.send(message_to_client(tts_stop))


async def reply_to_user_audio_input(websocket: ServerConnection):
    if len(user_audio_input) <= 0:
        return

    pcm_bytes = b""
    for opus in user_audio_input:
        pcm_bytes += opus_to_pcm(opus)
    user_input = audio_to_text(pcm_bytes)
    logger.info(f"Message from client {websocket.id}: {user_input}")

    await stream_audio_bytes(websocket, user_input)


async def handle_text_message(websocket: ServerConnection, msg: str):
    logger.debug(f"Message from client {websocket.id}: {msg}")
    m = message_from_client(msg)
    # handle different type of messages
    if m.type == MessageType.HELLO:
        await handshake(websocket)
    elif m.type == MessageType.LISTEN and m.state == AudioState.DETECT:
        await stream_audio_bytes(websocket, m.text)
    elif m.type == MessageType.LISTEN and m.state == AudioState.START:
        user_audio_input.clear()
        return
    elif m.type == MessageType.LISTEN and m.state == AudioState.STOP:
        await reply_to_user_audio_input(websocket)


async def handle_audio_message(opus_bytes: bytes):
    user_audio_input.append(opus_bytes)


async def handle_connection(websocket: ServerConnection):
    logger.success(f"Client connected: {websocket.id}")

    while True:
        try:
            msg = await websocket.recv()
            if isinstance(msg, str):
                await handle_text_message(websocket, msg)
            elif isinstance(msg, bytes):
                await handle_audio_message(msg)
        except ConnectionClosedOK:
            break

    logger.success(f"Client disconnected: {websocket.id}")
