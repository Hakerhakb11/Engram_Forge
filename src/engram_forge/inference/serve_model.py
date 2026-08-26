# serve_model.py — local HTTP inference server.
# Keeps LoRA in VRAM.
#
# POST /reply {"contact": "Alex", "messages": [{"role": "user", "content": "let's go to the gym"}, ...]}
#            -> {"reply": "I can't\nI have driving lessons"}

import argparse
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from unsloth import FastModel

from engram_forge.utils.get_json_config import load_config
from engram_forge.utils.get_user_config import (
    get_name,
    get_prompt_for_chatting,
)

HOST, PORT = "127.0.0.1", 8008

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent

MAX_SEQ_LEN = 1024
HISTORY_MAX = 20  # context replies (trained on 10)

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

my_name = get_name()
system_tmpl_with_facts = get_prompt_for_chatting()

parser = argparse.ArgumentParser(description="QLoRA train model")
parser.add_argument("--lora_name", type=str, default="lora_v2",
                    help="Name lora file")
args = parser.parse_args()


CONFIG_FILE: Path = PROJECT_DIR / "config/model_run_config.json"
DEFAULT_CONFIG = {
    "temperature": 0.5,
    "repetition_penalty": 1.14,
    "max_tokens": 400
}

config = load_config(CONFIG_FILE, DEFAULT_CONFIG)
temperature: float = config.get("temperature")
repeat_penalty: float = config.get("repetition_penalty")
max_tokens: int = config.get("max_tokens")


print("Loading model...")
LORA_DIR = os.path.join(PROJECT_DIR, "lora_adapters", args.lora_name)
model, tokenizer = FastModel.from_pretrained(
    model_name=LORA_DIR, max_seq_length=MAX_SEQ_LEN, load_in_4bit=True,
)
FastModel.for_inference(model)
tok = getattr(tokenizer, "tokenizer", tokenizer)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
if IM_END is None or IM_END == tok.unk_token_id:
    IM_END = tok.eos_token_id
GEN_LOCK = threading.Lock()  # Single GPU — generations are strictly queued


def clean_reply(text):
    """Removes thinking blocks, including unclosed ones (cut off by token limit)."""
    text = THINK_RE.sub("", text)
    if "</think>" in text:
        text = text.split("</think>")[-1]
    if "<think>" in text:
        text = text.split("<think>")[0]
    return text.strip()


def merge_roles(history):
    """Merges consecutive messages of the same role using \n —
    just like in the training dataset (role alternation is strictly required)."""
    merged = []
    for m in history:
        if merged and merged[-1]["role"] == m["role"]:
            merged[-1]["content"] += "\n" + m["content"]
        else:
            merged.append({"role": m["role"], "content": m["content"]})
    return merged


def generate_reply(contact, history, system_extra="", top_p=0.8):
    system = system_tmpl_with_facts.format(
        my_name=my_name, contact_name=contact)
    # RAG-memory: contact dossier + "what's going on with me right now" (stage 4)
    if system_extra:
        system += "\n\n" + system_extra
    messages = [{"role": "system", "content": system}]
    messages += merge_roles(history)[-HISTORY_MAX:]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False,  # empty <think></think>, just like in the training data
    )
    if not isinstance(prompt, str):  # rare processor wrapper glitch
        prompt = prompt[0] if isinstance(
            prompt, (list, tuple)) and prompt else str(prompt)
    inputs = tok(prompt, return_tensors="pt",
                 add_special_tokens=False).to(model.device)
    with GEN_LOCK:
        out = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repeat_penalty,
            do_sample=True,
            eos_token_id=IM_END,
            pad_token_id=IM_END,
        )
    reply = tok.decode(
        out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return clean_reply(reply)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/reply":
            self.send_error(404)
            return
        try:
            body = json.loads(self.rfile.read(
                int(self.headers["Content-Length"])))
            reply = generate_reply(body.get("contact") or "знакомый", body["messages"],
                                   body.get("system_extra", ""),
                                   float(body.get("top_p", 0.8)))
            data = json.dumps({"reply": reply},
                              ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:  # one bad request shouldn't crash the server  # noqa: BLE001
            print("Request error:", e)
            self.send_error(500, str(e))

    def log_message(self, fmt, *args):
        pass  # don't spam access log


if __name__ == "__main__":
    print(f"Server is ready: http://{HOST}:{PORT}/reply")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
