import os

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, SpeechSynthesizer


class CosyVoice:
    def __init__(self):
        dashscope.api_key = os.environ["ALIYUN_API_KEY"]
        self.model = os.environ["ALIYUN_TTS_MODEL"]
        self.voice = os.environ["ALIYUN_TTS_VOICE"]

    def synthesize(self, text: str) -> bytes:
        synthesizer = SpeechSynthesizer(model=self.model, voice=self.voice, format=AudioFormat.WAV_16000HZ_MONO_16BIT)
        return synthesizer.call(text)
