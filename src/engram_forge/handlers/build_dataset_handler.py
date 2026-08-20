from engram_forge.parser import build_dataset
from engram_forge.utils import sanitize_jsonl, split_dataset


def build_dataset_handler():

    print("\n You want to rewrite default name and prompt for dataset?\n"
          " ('yes' to Clear, 'Enter' to skip ")

    while True:
        choice = input(": ")
        match choice:
            case "yes":
                from engram_forge.handlers.set_default_handler import (
                    set_default_handler,
                )
                set_default_handler()
                break

            case "":
                break

            case _:
                break

    build_dataset.run()
    sanitize_jsonl.run()
    split_dataset.run()
