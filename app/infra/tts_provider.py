from typing import Generator

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, SpeechSynthesizer


class TTSProvider:
    def __init__(self, api_key: str, model: str):
        dashscope.api_key = api_key
        self.synthesizer = SpeechSynthesizer(
            model=model,
            voice="longxiaoxia_v2",
            format=AudioFormat.WAV_16000HZ_MONO_16BIT,
        )

    def text2speech(
        self, stream_text: Generator[str, None, None]
    ) -> Generator[bytes, None, None]:
        for text in stream_text:
            yield self.synthesizer.call(text)
