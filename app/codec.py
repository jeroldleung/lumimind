from typing import Generator

import opuslib


class Codec:
    def __init__(self):
        self.sample_rate = 16000
        self.channel = 1
        self.ms = 60
        self.fs = int(self.channel * self.sample_rate * self.ms / 1000)  # how many sample of a frame
        self.dec = opuslib.Decoder(self.sample_rate, self.channel)
        self.enc = opuslib.Encoder(self.sample_rate, self.channel, opuslib.APPLICATION_AUDIO)

    def decode(self, opus: bytes) -> bytes:
        return self.dec.decode(opus, self.fs)

    def encode(self, pcm: bytes) -> Generator[bytes, None, None]:
        # since the pcm is int16 bit depth, i.e., two bytes per sample,
        # so the audio bytes chunk size is fs * 2
        chunk_size = self.fs * 2
        for i in range(0, len(pcm), chunk_size):
            chunk = bytearray(chunk_size)
            chunk[:chunk_size] = pcm[i : i + chunk_size]
            opus = self.enc.encode(bytes(chunk), self.fs)
            yield opus
