import io
from typing import Generator

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, ResultCallback, SpeechSynthesizer
from loguru import logger


class CallBack(ResultCallback):
    _stream = None

    def on_open(self):
        self._stream = io.BytesIO()
        logger.info("TTS websocket client connection is opened")

    def on_complete(self):
        logger.info("Speech synthesis task complete successfully")

    def on_close(self):
        self._stream.close()
        logger.info("TTS websocket client connection is closed")

    def on_data(self, data: bytes) -> None:
        self._stream.write(data)


class TTSProvider:
    def __init__(self, api_key: str, model: str):
        dashscope.api_key = api_key
        self.callback = CallBack()
        self.synthesizer = SpeechSynthesizer(
            model=model,
            voice="longxiaoxia_v2",
            format=AudioFormat.PCM_16000HZ_MONO_16BIT,
            callback=self.callback,
        )

    def text2speech(self, stream_text: Generator[str, None, None]):
        for text in stream_text:
            self.synthesizer.streaming_call(text)
        self.synthesizer.streaming_complete()
