from pathlib import Path

from engram_forge.parser import build_dataset, sanitize_jsonl, split_dataset


def build_dataset_handler():

    print("\n You want to rewrite default name and prompt for dataset?\n"
          " ('yes' to Rewrite, 'Enter' to skip ")

    while True:
        choice = input(": ")
        match choice:
            case "yes":
                from engram_forge.handlers.set_prompt_handler import (
                    set_default_handler,
                )
                set_default_handler()
                break

            case "":
                break

            case _:
                break

    PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent

    build_dataset.run(PROJECT_DIR)
    sanitize_jsonl.run(PROJECT_DIR)
    split_dataset.run(PROJECT_DIR)
