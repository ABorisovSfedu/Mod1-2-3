from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./mod3.db"
    
    # API
    app_name: str = "Mod3-v1 - Visual Elements Mapping"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 9001
    
    # Matching settings
    fuzzy_threshold: float = 0.8
    max_components_per_section: int = 5
    max_matches: int = 6
    
    # Feature flags
    names_normalize: bool = True
    fallback_sections: bool = True
    require_props: bool = True
    dedup_by_component: bool = True
    at_least_one_main: bool = True
    
    # Template settings
    default_template: str = "hero-main-footer"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"


settings = Settings()

