import subprocess
import sys
from pathlib import Path

from engram_forge.handlers.inference_config_handler import (
    get_active_lora,
    select_lora_handler,
)
from engram_forge.handlers.model_configuration_handler import (
    model_configuration_handler,
)
from engram_forge.handlers.ui_helpers import clear_screen, pause

TEST_CHAT_PATH = Path(__file__).resolve().parent.parent / "inference/test_chat.py"
SERVE_MODEL_PATH = Path(__file__).resolve().parent.parent / "inference/serve_model.py"
EXPORT_GGUF_PATH = Path(__file__).resolve().parent.parent / "export/export_gguf.py"


def test_chat_run(active_lora: str):
    name = str(input("Type your name for this chat\n: ")).strip()
    if not name:
        print("[!] Name cannot be empty.")
        return

    command = [
        sys.executable,
        str(TEST_CHAT_PATH),
        "--contact", name,
        "--lora_name", active_lora,
    ]
    subprocess.run(command, check=True)


def serve_model_run(active_lora: str):
    command = [
        sys.executable,
        str(SERVE_MODEL_PATH),
        "--lora_name", active_lora,
    ]
    subprocess.run(command, check=True)


def export_gguf_model(active_lora: str):
    command = [
        sys.executable,
        str(EXPORT_GGUF_PATH),
        "--lora_name", active_lora,
    ]
    subprocess.run(command, check=True)


def model_inference_handler():
    while True:
        clear_screen()
        active_lora = get_active_lora()
        display_lora = active_lora if active_lora else "None (Select one first!)"

        print("\n=== Model Hub & Inference ===")
        print(f"\nActive LoRA: {display_lora}")
        print("\nWhat you want to do?"
              "\n1. Select Lora Adapter to use, or just show"
              "\n2. Model run configuration"
              "\n3. Test chat"
              "\n4. Serve model to HTTP server"
              "\n5. Export model as .gguf file"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                clear_screen()
                select_lora_handler()

            case "2":
                clear_screen()
                model_configuration_handler()

            case "3":
                clear_screen()
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                test_chat_run(active_lora)
                pause()

            case "4":
                clear_screen()
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                serve_model_run(active_lora)
                pause()

            case "5":
                clear_screen()
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                export_gguf_model(active_lora)
                pause()

            case "0":
                break

            case _:
                continue
