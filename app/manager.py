from loguru import logger
from websockets.asyncio.server import ServerConnection

from app.asr.sensevoice import SenseVoice
from app.chat.qwen import Qwen
from app.codec import Codec
from app.connection import Connection
from app.tts.cosyvoice import CosyVoice


class Manager:
    def __init__(self):
        self.asr = SenseVoice()
        self.chat = Qwen()
        self.tts = CosyVoice()
        self.codec = Codec()

    async def handle(self, conn: ServerConnection):
        logger.info(f"Open connection {conn.id}")
        c = Connection(conn, self.asr, self.chat, self.tts, self.codec)
        await c.route()
