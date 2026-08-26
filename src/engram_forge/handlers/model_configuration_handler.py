from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause
from engram_forge.utils.get_json_config import load_config, save_config

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent

CONFIG_FILE: Path = PROJECT_DIR / "config/model_run_config.json"
DEFAULT_CONFIG = {
    "temperature": 0.5,
    "repeat_penalty": 1.14,
    "max_tokens": 400
}


def input_float(message: str) -> float | None:
    user_input = input(message).strip()
    if not user_input:
        return None
    try:
        return float(user_input)
    except ValueError:
        print("[ERROR] Please enter a valid number (like 0.5)")
        return None


def input_int(message: str) -> int | None:
    user_input = input(message).strip()
    if not user_input:
        return None
    try:
        return int(user_input)
    except ValueError:
        print("[ERROR] Please enter a valid whole number (like 400)")
        return None


def model_configuration_handler():
    while True:
        config = load_config(CONFIG_FILE, DEFAULT_CONFIG)
        temperature: float = config.get("temperature")
        repeat_penalty: float = config.get("repeat_penalty")
        max_tokens: int = config.get("max_tokens")
        clear_screen()
        print("\nModel Run Configuration"
              "\nWhat you want to change?"
              f"\n1. temperature ({temperature})"
              f"\n2. repeat_penalty ({repeat_penalty})"
              f"\n3. tokens_count ({max_tokens})"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                temperature: float = input_float("New temperature: ")
                if temperature:
                    config["temperature"] = temperature
                    save_config(CONFIG_FILE, config)
                    pause()
                else:
                    pause()

            case "2":
                repeat_penalty: float = input_float("New repeat penalty: ")
                if repeat_penalty:
                    config["repeat_penalty"] = repeat_penalty
                    save_config(CONFIG_FILE, config)
                    pause()
                else:
                    pause()

            case "3":
                max_tokens: int = input_int("New tokens count: ")
                if max_tokens:
                    config["max_tokens"] = max_tokens
                    save_config(CONFIG_FILE, config)
                    pause()
                else:
                    pause()

            case "0":
                break

            case _:
                continue
