from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://mod3_user:mod3_password@localhost:5432/mod3_db"
    
    # API
    app_name: str = "Mod3-v1 - Visual Elements Mapping"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 9000
    
    # Matching settings
    fuzzy_threshold: float = 0.8
    max_components_per_section: int = 5
    
    # Template settings
    default_template: str = "hero-main-footer"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"


settings = Settings()

