from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import json

CONFIG_PATH = Path.home() / ".gclit" / "config.json"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=False
    )

    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4")
    api_key: str = Field(default="")
    lang: str = Field(default="en")

    @classmethod
    def load(cls) -> "AppConfig":
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        else:
            config = cls()
            config.save()
            return config

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)

    def update(self, key: str, value: str):
        if not hasattr(self, key):
            raise ValueError(f"Invalid config key: {key}")
        setattr(self, key, value)
        self.save()


settings = AppConfig.load()
