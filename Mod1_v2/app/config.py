from __future__ import annotations
import os, yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal

class LimitCfg(BaseSettings):
    max_duration_sec: int = 900
    max_file_mb: int = 25

class WhisperCfg(BaseSettings):
    model: str = Field(default=os.getenv("WHISPER_MODEL", "small"))
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "ru"
    vad_filter: bool = True
    temperature: float = 0.0

class ChunkingCfg(BaseSettings):
    sent_min: int = Field(default=int(os.getenv("CHUNK_SENT_MIN", 3)))
    sent_max: int = Field(default=int(os.getenv("CHUNK_SENT_MAX", 5)))
    char_limit: int = Field(default=int(os.getenv("CHUNK_CHAR_LIMIT", 1200)))
    overlap_sent: int = Field(default=int(os.getenv("OVERLAP_SENT", 1)))

class AppCfg(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = os.getenv("LOG_LEVEL", "info")
    save_raw_audio: bool = os.getenv("SAVE_RAW_AUDIO", "false").lower() == "true"
    emit_partial: bool = os.getenv("EMIT_PARTIAL", "true").lower() == "true"
    webhook_url: str | None = os.getenv("WEBHOOK_URL") or None
    tier: Literal['Basic','Extended','Premium'] = os.getenv("TIER", "Basic")
    stub_asr: bool = os.getenv("STUB_ASR", "false").lower() == "true"
    ws_debounce_ms: int = int(os.getenv("WS_DEBOUNCE_MS", "1200"))

class Settings(BaseSettings):
    db_url: str = os.getenv("DB_URL", "sqlite:///./data/asr.db")
    app: AppCfg = AppCfg()
    whisper: WhisperCfg = WhisperCfg()
    chunking: ChunkingCfg = ChunkingCfg()
    limits: dict[str, LimitCfg] = {
        "Basic": LimitCfg(),
        "Extended": LimitCfg(max_duration_sec=3600, max_file_mb=200),
        "Premium": LimitCfg(max_duration_sec=14400, max_file_mb=2048),
    }

    @staticmethod
    def from_yaml(path: str | None) -> "Settings":
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            s = Settings()
            if 'app' in data:
                for k, v in data['app'].items():
                    setattr(s.app, k, v)
            if 'whisper' in data:
                for k, v in data['whisper'].items():
                    setattr(s.whisper, k, v)
            if 'chunking' in data:
                for k, v in data['chunking'].items():
                    setattr(s.chunking, k, v)
            if 'limits' in data:
                for tier, vals in data['limits'].items():
                    s.limits[tier] = LimitCfg(**vals)
            return s
        return Settings()

CONFIG_FILE = os.getenv("CONFIG_FILE")
settings = Settings.from_yaml(CONFIG_FILE)