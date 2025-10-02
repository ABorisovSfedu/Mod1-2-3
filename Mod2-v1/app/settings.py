import os

class Settings:
    ingest_secret = os.getenv("INGEST_SECRET", "changeme")
    stream_preview = os.getenv("STREAM_PREVIEW", "false").lower() == "true"
    db_url = os.getenv("DB_URL", "sqlite:///./data/mod2.db")

settings = Settings()