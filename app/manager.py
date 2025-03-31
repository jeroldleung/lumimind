import asyncio

from loguru import logger
from websockets.asyncio.server import ServerConnection

from app.agent.qwen import Qwen
from app.asr.sensevoice import SenseVoice
from app.codec import Codec
from app.connection import Connection
from app.tts.cosyvoice import CosyVoice


class Manager:
    def __init__(self):
        self.asr = SenseVoice()
        self.agent = Qwen()
        self.tts = CosyVoice()
        self.codec = Codec()

    async def handle(self, conn: ServerConnection):
        logger.info(f"Open connection {conn.id}")
        c = Connection(conn, self.asr, self.agent, self.tts, self.codec)
        await asyncio.gather(c.consume(), c.produce())
        logger.info(f"Close connection {conn.id}")
