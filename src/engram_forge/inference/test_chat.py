# test_chat.py — Console chat with trained LoRA (smoke test after train_v2.py).
# You can write MULTIPLE messages in a row:
#   empty line — send all accumulated messages, /q — exit.

import argparse
import json
import os
import re
import sys
from pathlib import Path

from transformers import TextStreamer
from unsloth import FastModel

from engram_forge.utils.get_json_config import load_config
from engram_forge.utils.get_user_config import (
    get_name,
    get_prompt_for_chatting,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
MAX_SEQ_LEN = 1024

my_name = get_name()
system_tmpl_with_facts = get_prompt_for_chatting()

CONFIG_FILE: Path = PROJECT_DIR, "config/model_run_config.json"
DEFAULT_CONFIG = {
    "temperature": 0.5,
    "repeat_penalty": 1.14,
    "max_tokens": 400
}
config = load_config(CONFIG_FILE, DEFAULT_CONFIG)
temperature: float = config.get("temperature")
repeat_penalty: float = config.get("repeat_penalty")
max_tokens: int = config.get("max_tokens")


def clean_reply(text):
    THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
    """Removes thinking blocks, including unclosed ones (truncated by token limit),
    so they don't enter the dialogue history and ruin subsequent answers."""
    text = THINK_RE.sub("", text)
    if "</think>" in text:  # block was opened in the prompt
        text = text.split("</think>")[-1]
    if "<think>" in text:  # block is open but not closed — the rest is just thoughts
        text = text.split("<think>")[0]
    return text.strip()


def run(contact="friend", lora_name="lora_v2"):
    LORA_DIR = os.path.join(PROJECT_DIR, "lora_adapters", lora_name)
    model, tokenizer = FastModel.from_pretrained(
        model_name=LORA_DIR,
        max_seq_length=MAX_SEQ_LEN,
        load_in_4bit=True,
    )
    FastModel.for_inference(model)

    tok = getattr(tokenizer, "tokenizer", tokenizer)
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    if im_end is None or im_end == tok.unk_token_id:
        im_end = tok.eos_token_id
    streamer = TextStreamer(tok, skip_prompt=True, skip_special_tokens=True)

    messages = [{"role": "system", "content": system_tmpl_with_facts.format(
        my_name=my_name, contact_name=contact)}]
    print(f"\nChatting as: {my_name}, interlocutor: {contact}.")
    print("Type messages line by line; EMPTY line to send, /q to exit.\n")

    while True:
        lines = []
        while True:
            try:
                line = input(f"{contact}> ")
            except (EOFError, KeyboardInterrupt):
                line = "/q"
            if line.strip() == "/q":
                sys.exit(0)
            if line.strip() == "":
                if lines:
                    break
                continue  # empty line without accumulated messages — keep waiting
            lines.append(line.strip())

        messages.append({"role": "user", "content": "\n".join(lines)})

        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False,  # empty <think></think>, as in the training data
        )
        if not isinstance(prompt, str):
            # rare processor wrapper failure: save evidence and fix on the fly
            with open(os.path.join(PROJECT_DIR, "chat_debug.json"), "w", encoding="utf-8") as dbg:
                json.dump({"prompt_type": str(type(prompt)), "prompt_repr": repr(prompt)[:2000],
                           "messages": messages}, dbg, ensure_ascii=False, indent=2)
            print(
                f"[warn: template returned {type(prompt).__name__}, evidence saved to chat_debug.json]")
            prompt = prompt[0] if isinstance(
                prompt, (list, tuple)) and prompt else str(prompt)
        inputs = tok(prompt, return_tensors="pt",
                     add_special_tokens=False).to(model.device)

        print(f"{my_name}: ", end="", flush=True)
        out = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.8,
            top_k=40,
            repetition_penalty=repeat_penalty,
            do_sample=True,
            eos_token_id=im_end,
            pad_token_id=im_end,
            streamer=streamer,
        )
        prompt_len = inputs["input_ids"].shape[1]
        reply = tok.decode(out[0][prompt_len:], skip_special_tokens=True)
        reply = clean_reply(reply)
        messages.append({"role": "assistant", "content": reply})
        print()

        # prevent context from growing infinitely
        if len(messages) > 21:
            messages = [messages[0]] + messages[-20:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA train model")

    parser.add_argument("--contact", type=str, default="friend",
                        help="Contact name")

    parser.add_argument("--lora_name", type=str, default="lora_v2",
                        help="Name lora file")

    args = parser.parse_args()
    run(contact=args.contact, lora_name=args.lora_name)
