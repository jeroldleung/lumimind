from typing import Generator

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, ResultCallback, SpeechSynthesizer
from loguru import logger


class CallBack(ResultCallback):
    byte_queue = None

    def on_open(self) -> None:
        self.byte_queue = []
        logger.info("TTS websocket connection is opened")

    def on_data(self, data: bytes) -> None:
        self.byte_queue.append(data)

    def on_close(self) -> None:
        logger.info("TTS websocket connection is closed")


class TTSProvider:
    def __init__(self, api_key: str, model: str):
        dashscope.api_key = api_key
        self.model = model
        self.callback = CallBack()

    def text2speech(
        self, stream_text: Generator[str, None, None]
    ) -> Generator[bytes, None, None]:
        synthesizer = SpeechSynthesizer(
            model=self.model,
            voice="longxiaoxia_v2",
            format=AudioFormat.WAV_16000HZ_MONO_16BIT,
            callback=self.callback,
        )
        for text in stream_text:
            synthesizer.streaming_call(text)
        synthesizer.streaming_complete()

        for chunk in self.callback.byte_queue:
            yield chunk
