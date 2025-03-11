from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str

    ASR_LOCAL_PATH: str

    TTS_API_KEY: str
    TTS_MODEL: str

    IOT_SERVICE_URL: str
