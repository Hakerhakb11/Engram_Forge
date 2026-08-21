import subprocess
import sys
from pathlib import Path

from engram_forge.handlers.inference_config_handler import (
    get_active_lora,
    select_lora_handler,
)
from engram_forge.handlers.ui_helpers import clear_screen, pause

TEST_CHAT_PATH = Path(__file__).resolve().parent.parent / "test_chat.py"
SERVE_MODEL_PATH = Path(__file__).resolve().parent.parent / "serve_model.py"


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


def model_inference_handler():
    while True:
        clear_screen()
        active_lora = get_active_lora()
        display_lora = active_lora if active_lora else "None (Select one first!)"

        print("\n=== Model Hub & Inference ===")
        print(f"\nActive LoRA: {display_lora}")
        print("\nWhat you want to do?"
              "\n1. Select Lora Adapter to use, or just show"
              "\n2. Test chat"
              "\n3. Serve model to HTTP server"
              "\n4. Export model as .gguf file"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                select_lora_handler()

            case "2":
                clear_screen()
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                test_chat_run(active_lora)
                pause()

            case "3":
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                serve_model_run(active_lora)
                pause()

            case "4":
                if not active_lora:
                    print("\n[!] Please select a LoRA adapter first.")
                    pause()
                    continue
                from engram_forge.export_gguf import export_gguf_model  # type: ignore
                export_gguf_model(active_lora)#TODO
                pause()

            case "0":
                break

            case _:
                continue
