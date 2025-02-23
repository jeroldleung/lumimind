from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    HELLO = "hello"
    LISTEN = "listen"
    TTS = "tts"
    ABORT = "abort"
    IOT = "iot"
    LLM = "llm"


class MessageToDevice(BaseModel):
    type: MessageType
    transport: str | None = None
    audio_params: dict[str, int] | None = None
    state: str | None = None
    text: str | None = None
    emotion: str | None = None


class MessageFromDevice(BaseModel):
    type: MessageType
    version: int | None = None
    transport: str | None = None
    audio_params: dict[str, str | int] | None = None
    session_id: str | None = None
    state: str | None = None
    mode: str | None = None
    text: str | None = None
    reason: str | None = None


def message_to_device(
    *,
    type: MessageType,
    state: str | None = None,
    text: str | None = None,
    emotion: str | None = None,
) -> str:
    m = MessageToDevice(type=type)

    if type == MessageType.HELLO:
        m.transport = "websocket"
        m.audio_params = {"sample_rate": 1600}
    elif type == MessageType.TTS:
        m.state = state
        m.text = text
    elif type == MessageType.LLM:
        m.emotion = emotion

    return m.model_dump_json(exclude_none=True)


def message_from_device(msg: str) -> MessageFromDevice:
    return MessageFromDevice.model_validate_json(msg)
