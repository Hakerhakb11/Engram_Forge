from engram_forge import build_dataset
from engram_forge.utils import sanitize_jsonl

if __name__ == "__main__":

    build_dataset.setUserName(input("Enter your name: ") or "Me")
    build_dataset.run()
    sanitize_jsonl.run()
