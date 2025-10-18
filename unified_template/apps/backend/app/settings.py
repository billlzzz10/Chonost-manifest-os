from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    sqlite_path: str = '.runtime/storage.db'
    vector_cache_path: str = '.runtime/vectors.db'
    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'qwen2.5-coder'
    agent_max_steps: int = 8

    @property
    def sqlite_path_resolved(self) -> Path:
        return Path(self.sqlite_path)

settings = Settings()

