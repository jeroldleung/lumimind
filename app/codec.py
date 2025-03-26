from io import BytesIO
from typing import Generator

import numpy as np
import opuslib
import soundfile as sf
from pydub import AudioSegment


class Codec:
    def __init__(self, sample_rate: int, channel: int, ms: int):
        self.sample_rate = sample_rate
        self.channel = channel
        self.ms = ms
        self.fs = int(self.channel * self.sample_rate * self.ms / 1000)
        self.dec = opuslib.Decoder(self.sample_rate, self.channel)
        self.enc = opuslib.Encoder(self.sample_rate, self.channel, opuslib.APPLICATION_AUDIO)

    def decode(self, opus: bytes) -> bytes:
        return self.dec.decode(opus, self.fs)

    def encode(self):
        pass

    def wav_to_opus(self, audio_bytes: bytes) -> Generator[bytes, None, None]:
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        wav_buf = BytesIO()
        sf.write(wav_buf, audio_np, samplerate=16000, format="wav")
        audio = AudioSegment.from_file(wav_buf, format="wav")  # load wav data
        audio.set_channels(1).set_frame_rate(16000)
        encoder = opuslib.Encoder(16000, 1, opuslib.APPLICATION_AUDIO)

        frame_duration = 60  # 60ms per frame
        frame_size = int(16000 * frame_duration / 1000)
        raw_data = audio.raw_data

        for i in range(0, len(raw_data), frame_size * 2):
            chunk = raw_data[i : i + frame_size * 2]
            if len(chunk) < frame_size * 2:
                chunk += b"\x00" * (frame_size * 2 - len(chunk))
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            opus_data = encoder.encode(np_frame.tobytes(), frame_size)
            yield opus_data
