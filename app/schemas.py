from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    HELLO = "hello"
    LISTEN = "listen"
    TTS = "tts"
    ABORT = "abort"
    IOT = "iot"
    LLM = "llm"


class AudioState(Enum):
    START = "start"
    STOP = "stop"
    DETECT = "detect"
    SENTENCE_START = "sentence_start"


class MessageToClient(BaseModel):
    type: MessageType
    transport: str | None = "websocket"
    audio_params: dict[str, int] | None = {"sample_rate": 16000}
    state: AudioState | None = None
    text: str | None = None
    emotion: str | None = None


class MessageFromClient(BaseModel):
    type: MessageType
    version: int | None = None
    transport: str | None = None
    audio_params: dict[str, str | int] | None = None
    session_id: str | None = None
    state: AudioState | None = None
    mode: str | None = None
    text: str | None = None
    reason: str | None = None
