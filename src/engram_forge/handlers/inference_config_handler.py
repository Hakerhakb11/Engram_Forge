import json
from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = PROJECT_DIR / "config" / "inference_config.json"
LORA_DIR = PROJECT_DIR / "lora_adapters"


def get_active_lora() -> str | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("active_lora")
    except json.JSONDecodeError:
        return None


def set_active_lora(lora_name: str):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                pass

    config["active_lora"] = lora_name

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def select_lora_handler():
    if not LORA_DIR.exists() or not any(LORA_DIR.iterdir()):
        print("\n[!] No LoRA adapters found in 'lora_adapters/' folder.")
        print("You need to train a model first.")
        return

    adapters = [d.name for d in LORA_DIR.iterdir() if d.is_dir()]

    if not adapters:
        print("\n[!] No LoRA adapter folders found.")
        return

    while True:
        clear_screen()

        print("\nAvailable LoRA Adapters:")
        for i, adapter_name in enumerate(adapters, 1):
            print(f"{i}. {adapter_name}")

        choice = input(
            "Select adapter number (Enter to cancel): ").strip()

        if not choice:
            return

        if choice.isdigit() and 1 <= int(choice) <= len(adapters):
            selected = adapters[int(choice) - 1]
            set_active_lora(selected)
            print(
                f"\nSet '{selected}' active LoRA adapter")
            pause()
            break
        else:
            print("[ERROR] Invalid choice. Try again.")
            pause()
