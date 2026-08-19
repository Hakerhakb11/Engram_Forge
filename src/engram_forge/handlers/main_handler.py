import os
import platform
from pathlib import Path


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_os_for_training() -> bool:
    current_os = platform.system()

    if current_os != "Linux":
        print("\n[ERROR] Train are impossible!")
        print(f"Your oS: {current_os}.")
        print("Library Unsloth and CUDA Settings requires Linux")
        print("Please, run Engram Forge from WSL for training.")
        return False

    return True


def main_handler():
    while True:
        clear_screen()
        print("\nWelcome to Engram Forge!"
              "\nWhat you want to do?"
              "\n1. Start"
              "\n2. Import Telegram chats - (result.json) or WhatsApp chat - (*.txt)"
              "\n3. Show imported chats"
              "\n4. Set default name and prompt for dataset"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                if check_os_for_training():
                    from engram_forge.handlers.train_handler import train_handler
                    train_handler()

            case "2":
                from engram_forge.handlers.import_handler import import_handler
                clear_screen()
                import_handler()
                input("\nPress Enter to return...")

            case "3":
                clear_screen()
                print("\nImported chats:")
                chats_dir = Path("chats")
                if not chats_dir.exists():
                    print(f"{chats_dir} directory not found. Creating...")
                    chats_dir.mkdir(parents=True, exist_ok=True)
                    print(f"{chats_dir} directory created.")
                    print("Pleace import some chat files.")
                    input("\nPress Enter to return...")
                    continue

                for filepath in chats_dir.iterdir():
                    if not filepath.is_file():
                        print(f"Skipping {filepath.name}: Not a file.")
                        continue

                    if filepath.suffix == ".json":
                        print(f"- {filepath.name} (Telegram .json)")
                    elif filepath.suffix == ".txt":
                        print(f"- {filepath.name} (WhatsApp .txt)")

                input("\nPress Enter to return...")
            case "4":
                from engram_forge.handlers.set_default_handler import (
                    set_default_handler,
                )
                set_default_handler()
                input("\nPress Enter to return...")

            case "0":
                print("\nExiting...")
                break

            case _:
                continue
