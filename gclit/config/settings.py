from config.config_manager import load_config

class Settings:
    def __init__(self):
        self._config = load_config()

    @property
    def provider(self):
        return self._config.get("provider")

    @property
    def model(self):
        return self._config.get("model")

    @property
    def api_key(self):
        return self._config.get("api_key")

    @property
    def lang(self):
        return self._config.get("lang")

settings = Settings()
