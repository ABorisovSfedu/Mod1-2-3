from __future__ import annotations
from typing import Any, Dict, Literal
from pathlib import Path
import yaml

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)

CONFIG_DIR = Path(__file__).resolve().parent
YAML_PATH = CONFIG_DIR / "app.yaml"


class YamlSettingsSource(PydanticBaseSettingsSource):
    """
    Источник настроек из YAML для pydantic-settings v2.
    Реализуем оба обязательных метода: __call__ и get_field_value.
    """
    def __init__(self, settings_cls, yaml_path: Path | None = None):
        super().__init__(settings_cls)
        self.yaml_path = yaml_path or YAML_PATH
        self._data: Dict[str, Any] = {}
        if self.yaml_path.exists():
            try:
                loaded = yaml.safe_load(self.yaml_path.read_text(encoding="utf-8")) or {}
                if isinstance(loaded, dict):
                    self._data = loaded
            except Exception:
                # Если не удалось прочитать YAML — просто игнорируем
                self._data = {}

    def __call__(self) -> Dict[str, Any]:
        # Полная «карта» значений (используется Pydantic при сборке настроек)
        return dict(self._data)

    def get_field_value(self, field, field_name: str):
        """
        Возвращаем (value, source) либо (None, None).
        Ищем по alias и по имени поля в разных регистрах.
        """
        keys: list[str] = []
        if field.alias:
            a = str(field.alias)
            keys.extend([a, a.lower(), a.upper()])
        keys.extend([field_name, field_name.lower(), field_name.upper()])

        for k in keys:
            if k in self._data:
                return self._data[k], "yaml"
        return None, None


class Settings(BaseSettings):
    # — App meta —
    app_name: str = Field(default="Module 2 - NLP & Layout Service")

    # — NLP / Mapping —
    stanza_lang: str = Field(default="ru", alias="STANZA_LANG")
    fuzzy_threshold: float = Field(default=0.80, alias="FUZZY_THRESHOLD")
    stream_preview: bool = Field(default=True, alias="STREAM_PREVIEW")

    # — Layout —
    page_template: str = Field(default="hero-main-footer", alias="PAGE_TEMPLATE")
    max_components_per_page: int = Field(default=12, alias="MAX_COMPONENTS_PER_PAGE")

    # — Tiers —
    plan: Literal["BASIC", "EXTENDED", "PREMIUM"] = Field(default="EXTENDED", alias="PLAN")

    # — Server —
    environment: str = Field(default="dev")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,   # чтобы алиасы из ENV подхватывались
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,                 # важно для v2
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        # Приоритет источников: ENV > YAML > init kwargs > .env > secrets
        yaml_source = YamlSettingsSource(settings_cls)
        return (
            env_settings,
            yaml_source,
            init_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
