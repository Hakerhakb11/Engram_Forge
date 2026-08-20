
from engram_forge.handlers.main_handler import clear_screen


def handle_checkpoint_cleanup():
    """Checks existence of old checkpoints and offers to clear them"""
    import os
    import shutil
    OUT_DIR = os.path.expanduser("~/tgstyle/out")
    if OUT_DIR.exists() and any(OUT_DIR.iterdir()):
        print(f"\n[!] Found existing checkpoints in: {OUT_DIR}")
        choice = (
            input(
                "\n[ALERT]If you change your dataset or model for train, YOU NEED TO CLEAR PREVIOUS CHECKPOINTS"
                "CLEAR previous checkpoints and start from scratch?" \
                " ('yes' to Clear, 'Enter' to skip ")
            .strip()
            .lower()
        )

        if choice == "yes":
            shutil.rmtree(OUT_DIR)
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            print("Checkpoint directory successfully cleaned!")
        else:
            print("Keeping checkpoints. Training will resume from the last step.")


def train_run_handler():
    import subprocess
    import sys

    from engram_forge.handlers.model_config_handler import (
        get_epochs_count,
        get_lora_name,
        get_model_name,
    )

    command = [
        sys.executable,
        "src/engram_forge/train_v2.py",
        "--model", get_model_name(),
        "--epochs", str(get_epochs_count()),
        "--lora_name", get_lora_name()
    ]

    subprocess.run(command, check=True)


def train_handler():
    while True:
        clear_screen()
        print("What you want to do?"
              "\n1. Start training"
              "\n2. Build Dataset"
              "\n3. Change train config"
              "\n0. Exit")

        choice = input(": ")
        match choice:
            case "1":
                train_run_handler()
                print("\nTraining process finished!")
                input("\nPress Enter to return...")

            case "2":
                from engram_forge.handlers.build_dataset_handler import (
                    build_dataset_handler,
                )
                build_dataset_handler()
                input("\nPress Enter to return...")

            case "3":
                from engram_forge.handlers.model_config_handler import (
                    change_epochs_count_handler,
                    change_lora_name_handler,
                    change_model_handler,
                )

                change_epochs_count_handler()
                change_lora_name_handler()
                change_model_handler()
                input("\nPress Enter to return...")

            case "0":
                print("\nExiting...")
                break

            case _:
                continue
