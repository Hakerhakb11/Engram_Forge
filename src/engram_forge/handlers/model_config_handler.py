import json
from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause
from engram_forge.hugging_face_api import search_model

CONFIG_FILE = Path("config/train_config.json")
DEFAULT_CONFIG = {
    "selected_model": "unsloth/Qwen3.5-4B",
    "epochs_count": 2,
    "lora_name": "lora_v2"
}


def load_config() -> dict:
    """Universal config loading with automatic creation default values"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not CONFIG_FILE.exists():
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config_data: dict):
    """Universal config saving."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config_data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def get_model_name() -> str:
    return load_config().get("selected_model", DEFAULT_CONFIG["selected_model"])


def get_epochs_count() -> int:
    return load_config().get("epochs_count", DEFAULT_CONFIG["epochs_count"])


def get_lora_name() -> str:
    return load_config().get("lora_name", DEFAULT_CONFIG["lora_name"])


def remove_bad_models(raw_models) -> list:
    bad_keywords = ["gguf", "awq", "gptq", "exl2",
                            "onnx", "openvino", "lora", "adapter"]

    models = []
    for m in raw_models:
        model_name = m.get('id', '').lower()

        is_bad = any(bad_word in model_name for bad_word in bad_keywords)

        if not is_bad:
            models.append(m)

    return models


def change_model_handler():
    default_model = get_model_name()
    while True:
        clear_screen()
        print("Put search query (Enter to skip)\n"
              "recommended: 'unsloth/Qwen3.5-4B'")
        query = input(f"now: '{default_model}': ").strip()

        if not query:
            print("Cancelled.")
            return

        print(f"\n🔍 Searching for '{query}' on HuggingFace...")

        try:
            raw_models = search_model(query)
        except Exception as e:  # noqa: BLE001
            print(
                f"\n[ERROR] Failed to fetch models from HuggingFace API: {e}")
            continue

        models = remove_bad_models(raw_models)

        print("\nFound models:")
        for i, model in enumerate(models[:10], 1):
            model_id = model.get("id", "Unknown")
            downloads = model.get("downloads", 0)
            print(f"  {i}. {model_id} ({downloads:,} downloads)")

        if not models:
            print("\nNo models found matching your query.")
            pause()
            continue

        choice = input(
            "\nSelect model number (Enter to cancel): ").strip().lower()

        if not choice:
            continue

        selected_model = None

        try:
            index = int(choice) - 1
            if 0 <= index < len(models):
                selected_model = models[index]["id"]
            else:
                print("[ERROR] Invalid number selection.")
                pause()
                continue
        except ValueError:
            print("[ERROR] Invalid input.")
            pause()
            continue

        if not selected_model:
            print("No selected model was found")
            pause()
            continue
        break

    config = load_config()
    config["selected_model"] = selected_model
    save_config(config)

    print(f"\nModel successfully saved to config: {selected_model}")


def change_epochs_count_handler():
    default_epochs_count = get_epochs_count()
    while True:
        clear_screen()
        print("Enter new epochs count (Enter to skip)\n"
              "recommended: ")
        epochs_val = input(f"now: '{default_epochs_count}': ")

        if not epochs_val:
            print("Cancelled.")
            return

        if not epochs_val.isdigit():
            print("[ERROR] Invalid input.")
            pause()
            continue
        else:
            break

    config = load_config()
    config["epochs_count"] = epochs_val
    save_config(config)

    print(f"\nEpochs successfully saved: {epochs_val}")


def change_lora_name_handler():
    default_lora_name = get_lora_name()
    clear_screen()
    print("Change lora file name (Enter to skip)\n")
    input_lora_name = input(f"now: '{default_lora_name}': ").strip()

    if not input_lora_name:
        print("Cancelled.")
        return

    config = load_config()
    config["lora_name"] = input_lora_name
    save_config(config)

    print(f"\nLoRA name successfully saved: {input_lora_name}")
