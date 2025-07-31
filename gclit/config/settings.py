# config/settings.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, TypeAdapter
import json

from gclit.domain.models.common import Lang

CONFIG_PATH = Path.home() / ".gclit" / "config.json"


class OpenAISettings(BaseModel):
    api_key: str = ""


class ClaudeSettings(BaseModel):
    api_key: str = ""


class LocalSettings(BaseModel):
    endpoint: str = "http://localhost:11434"


class GitHubSettings(BaseModel):
    token: str = ""


class AzureDevOpsSettings(BaseModel):
    token: str = ""


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GCLIT_",
        env_nested_delimiter="__",
        extra="ignore"
    )

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    lang: Lang = "en"

    # Git providers
    github: GitHubSettings = GitHubSettings()
    azure_devops: AzureDevOpsSettings = AzureDevOpsSettings()

    # LLMs providers
    openai: OpenAISettings = OpenAISettings()
    claude: ClaudeSettings = ClaudeSettings()
    local: LocalSettings = LocalSettings()

    @classmethod
    def load(cls) -> "AppConfig":
        env_config = cls()

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_config = json.load(f)
            # return cls(**file_config)
            return TypeAdapter(cls).validate_python(file_config)
        else:
            # env_config.save()
            return env_config

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)

    def update(self, key: str, value: str):
        current_data = self.model_dump()

        ref = current_data
        parts = key.split(".")
        for part in parts[:-1]:
            if part not in ref or not isinstance(ref[part], dict):
                ref[part] = {}
            ref = ref[part]
        ref[parts[-1]] = value

        updated = TypeAdapter(AppConfig).validate_python(current_data)

        # Guardar y reemplazar atributos
        updated.save()

        # ⚠️ Retorna la instancia actualizada
        return updated


def get_config_keys(config: BaseModel, prefix="") -> list[str]:
    keys = []
    for field, value in config.model_dump().items():
        full_key = f"{prefix}.{field}" if prefix else field
        if isinstance(value, dict):
            keys.extend(get_config_keys(BaseModel.model_validate(value), prefix=full_key))
        else:
            keys.append(full_key)
    return keys


settings = AppConfig.load()
