from enum import Enum
from typing import Any, Dict, List

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


class ListeningMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    REALTIME = "realtime"


class MessageOut(BaseModel):
    type: MessageType
    transport: str | None = None
    audio_params: Dict[str, int] | None = None
    state: AudioState | None = None
    text: str | None = None
    emotion: str | None = None
    commands: List[Dict[str, Any]] | None = None


class MessageIn(BaseModel):
    type: MessageType
    version: int | None = None
    transport: str | None = None
    audio_params: Dict[str, str | int] | None = None
    session_id: str | None = None
    state: AudioState | None = None
    mode: ListeningMode | None = None
    text: str | None = None
    reason: str | None = None
