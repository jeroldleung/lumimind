from typing import Generator

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, SpeechSynthesizer


class TTSProvider:
    def __init__(self, api_key: str, model: str):
        dashscope.api_key = api_key
        self.model = model

    def text2speech(
        self, stream_text: Generator[str, None, None]
    ) -> Generator[bytes, None, None]:
        synthesizer = SpeechSynthesizer(
            model=self.model,
            voice="longxiaoxia_v2",
            format=AudioFormat.WAV_16000HZ_MONO_16BIT,
        )
        for text in stream_text:
            yield synthesizer.call(text)
