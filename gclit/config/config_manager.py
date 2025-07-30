import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".gclit" / "config.json"

DEFAULT_CONFIG = {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "",
    "lang": "en"
}

def load_config():
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_config(key, value):
    config = load_config()
    config[key] = value
    save_config(config)

def get_config_value(key):
    return load_config().get(key)
