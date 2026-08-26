from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause

TRAIN_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "train_v2.py"


def handle_checkpoint_cleanup():
    """Checks existence of old checkpoints and offers to clear them"""
    import shutil
    out_dir = Path("~/tgstyle/out").expanduser()
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"\n[!] Found existing checkpoints in: {out_dir}")
        choice = (
            input(
                "\n[ALERT]If you change your dataset or model for train, YOU NEED TO CLEAR PREVIOUS CHECKPOINTS"
                "CLEAR previous checkpoints and start from scratch?"
                " ('yes' to Clear, 'Enter' to skip ")
            .strip()
            .lower()
        )

        if choice == "yes":
            shutil.rmtree(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            print("Checkpoint directory successfully cleaned!")
        else:
            print("Keeping checkpoints. Training will resume from the last step.")


def train_run_handler():
    import subprocess
    import sys

    from engram_forge.handlers.train_config_handler import (
        get_epochs_count,
        get_lora_name,
        get_model_name,
    )

    handle_checkpoint_cleanup()

    command = [
        sys.executable,
        str(TRAIN_SCRIPT_PATH),
        "--model", get_model_name(),
        "--epochs", str(get_epochs_count()),
        "--lora_name", get_lora_name()
    ]

    subprocess.run(command, check=True)


def train_handler():
    while True:
        clear_screen()
        print("\n=== Training menu ===")
        print("What you want to do?"
              "\n1. Start training"
              "\n2. Build Dataset"
              "\n3. Change train config"
              "\n4. Change name, and prompt for dataset"
              "\n0. Exit")

        choice = input(": ")
        match choice:
            case "1":
                train_run_handler()
                print("\nTraining process finished!")
                pause()

            case "2":
                from engram_forge.handlers.build_dataset_handler import (
                    build_dataset_handler,
                )
                build_dataset_handler()
                pause()

            case "3":
                from engram_forge.handlers.train_config_handler import (
                    change_epochs_count_handler,
                    change_lora_name_handler,
                    change_model_handler,
                )

                change_epochs_count_handler()
                change_lora_name_handler()
                change_model_handler()

            case "4":
                from engram_forge.handlers.set_prompt_handler import (
                    set_name_base_prompt_handler,
                )
                set_name_base_prompt_handler()

            case "0":
                print("\nExiting...")
                break

            case _:
                continue
