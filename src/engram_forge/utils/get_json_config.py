import json
from pathlib import Path


def load_config(CONFIG_FILE: Path, DEFAULT_CONFIG: dict) -> dict:
    """Universal config loading with automatic creation default values"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not CONFIG_FILE.exists():
            save_config(CONFIG_FILE, DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        save_config(CONFIG_FILE, DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(CONFIG_FILE: Path, config_data: dict) -> None:
    """Universal config saving."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config_data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
