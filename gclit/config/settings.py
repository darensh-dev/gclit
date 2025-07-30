# config/settings.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, TypeAdapter
import json

CONFIG_PATH = Path.home() / ".gclit" / "config.json"


class OpenAISettings(BaseModel):
    api_key: str = ""


class ClaudeSettings(BaseModel):
    api_key: str = ""


class LocalSettings(BaseModel):
    endpoint: str = "http://localhost:11434"


class ProvidersConfig(BaseModel):
    openai: OpenAISettings = OpenAISettings()
    claude: ClaudeSettings = ClaudeSettings()
    local: LocalSettings = LocalSettings()


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GCLIT_",
        env_nested_delimiter="__",
        extra="ignore"
    )

    provider: str = "openai"
    model: str = "gpt-4o"
    lang: str = "en"
    providers: ProvidersConfig = ProvidersConfig()

    @classmethod
    def load(cls) -> "AppConfig":
        env_config = cls()

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_config = json.load(f)
            # return cls(**file_config)
            return TypeAdapter(cls).validate_python(file_config)
        else:
            env_config.save()
            return env_config

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)

    # def update(self, key: str, value: str):
    #     if key in self.model_dump():
    #         setattr(self, key, value)
    #     elif "." in key:
    #         parts = key.split(".")
    #         ref = self
    #         for part in parts[:-1]:
    #             ref = getattr(ref, part)
    #         setattr(ref, parts[-1], value)
    #     else:
    #         raise ValueError(f"Invalid config key: {key}")
    #     self.save()

    def update(self, key: str, value: str):
        # Dump actual config a dict
        current_data = self.model_dump()

        # 🔧 Modificar el dict (anidado si es necesario)
        ref = current_data
        parts = key.split(".")
        for part in parts[:-1]:
            if part not in ref or not isinstance(ref[part], dict):
                ref[part] = {}
            ref = ref[part]
        ref[parts[-1]] = value

        # 🔄 Revalidar todo el config con tipado correcto
        updated = TypeAdapter(AppConfig).validate_python(current_data)

        # Guardar y reemplazar atributos
        updated.save()

        # ⚠️ Retorna la instancia actualizada
        return updated


settings = AppConfig.load()
