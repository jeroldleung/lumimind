from app.config import settings
from app.infra import ASRProvider, TTSProvider
from app.services import AudioService
from app.utils.stream import stream_content

asr_client = ASRProvider(local_path=settings.ASR_LOCAL_PATH)
tts_client = TTSProvider(settings.TTS_API_KEY, settings.TTS_MODEL)
audio_service = AudioService(asr_client, tts_client)


def test_text_to_speech():
    text = "How is going today"
    text_stream = stream_content(text)
    audio_bytes = []
    audio_bytes_stream = audio_service.text2speech(text_stream)
    for ab in audio_bytes_stream:
        audio_bytes.append(ab)
    res = audio_service.speech2text(audio_bytes).lower()
    assert res
