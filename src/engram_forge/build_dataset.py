# build_dataset.py — export Telegram (result.json) -> dataset (dataset.jsonl)

import json
import re

import ijson

from engram_forge.utils.user_id_finder import user_id_finder

SESSION_GAP = 4 * 3600      # gap of more than 4 hours = new dialog
BURST_GAP = 300             # same author after a pause >5 min = new dialog
MAX_TURN_MSGS = 6           # maximum messages in one turn
MAX_MSG_LINES = 10          # "paste" messages (lists, logs, code) limit
MAX_MSG_CHARS = 1200        # "paste" messages (lists, logs, code) limit
MAX_TURNS = 10              # maximum turns in one example
MAX_CHARS = 3000            # maximum length of an example
MIN_MY_TURNS = 1            # there must be at least one reply from me
MIN_PARTNER_TURNS = 1       # and at least one reply from the partner

MY_NAME = "Me"              # Default name for the user

multi_nl_re = re.compile(r"\n{3,}")
spaces_re = re.compile(r"[ \t]+")


def normalize_text(t):
    if t is None:
        return ""
    if isinstance(t, str):
        s = t
    elif isinstance(t, list):
        parts = []
        for x in t:
            if isinstance(x, str):
                parts.append(x)
            elif isinstance(x, dict) and "text" in x:
                parts.append(str(x["text"]))
        s = "".join(parts)
    else:
        s = str(t)
    s = s.replace("\r", "")
    s = spaces_re.sub(" ", s)
    s = multi_nl_re.sub("\n\n", s)
    return s.strip()


def media_placeholder(msg):
    """Text placeholder instead of media: [sticker 😂], [photo], [voice]"""
    mt = msg.get("media_type")
    if mt == "sticker":
        emoji = str(msg.get("sticker_emoji") or "").strip()
        return f"[sticker {emoji}]" if emoji else "[sticker]"
    named = {
        "voice_message": "[voice]",
        "video_message": "[video message]",
        "animation": "[gif]",
        "video_file": "[video]",
        "audio_file": "[audio]",
    }
    if mt in named:
        return named[mt]
    if "photo" in msg:
        return "[photo]"
    if "contact_information" in msg:
        return "[contact]"
    if "location_information" in msg:
        return "[location]"
    if "file" in msg:
        return "[file]"
    return None


def iter_messages(chat, my_from_id):
    """Yields (is_me, text, unixtime) for meaningful chat messages.
    Partner's media is marked with a placeholder."""
    for msg in chat.get("messages", []):
        if msg.get("type") != "message":
            continue
        from_id = msg.get("from_id")
        if not from_id:
            continue
        is_me = from_id == my_from_id
        forwarded = msg.get("forwarded_from") is not None

        if is_me and forwarded:
            continue

        text = normalize_text(msg.get("text"))
        if text and (text.count("\n") + 1 > MAX_MSG_LINES or len(text) > MAX_MSG_CHARS):
            continue

        ph = media_placeholder(msg)

        if is_me:
            if not text:
                continue
        else:
            if ph:
                text = f"{ph} {text}".strip() if text else ph
            if forwarded:
                text = f"[forwarded] {text}" if text else "[forwarded message]"
            if not text:
                continue

        try:
            t = int(msg.get("date_unixtime"))
        except (TypeError, ValueError):
            continue
        yield (is_me, text, t)


def split_sessions(messages):
    """Splits the message stream into sessions."""
    session = []
    prev_t = None
    prev_is_me = None
    for m in messages:
        is_me, _text, t = m
        gap = None if prev_t is None else t - prev_t
        if gap is not None and (
            gap > SESSION_GAP or (is_me == prev_is_me and gap > BURST_GAP)
        ):
            if session:
                yield session
            session = []
        session.append(m)
        prev_t = t
        prev_is_me = is_me
    if session:
        yield session


def to_turns(session):
    """Concatenates consecutive messages into a single turn separated by \\n."""
    turns = []  # (is_me, text, n_msgs)
    for is_me, text, _t in session:
        if turns and turns[-1][0] == is_me:
            if turns[-1][2] < MAX_TURN_MSGS:
                turns[-1] = (is_me, turns[-1][1] + "\n" +
                             text, turns[-1][2] + 1)
        else:
            turns.append((is_me, text, 1))
    return [(is_me, text) for is_me, text, _n in turns]


def to_windows(turns):
    """Splits a list of turns into non-overlapping windows.
    The tail of partner's replies is carried over to the next window,
    so that each window ends with my reply."""
    windows = []
    cur = []
    cur_chars = 0
    for turn in turns:
        cur.append(turn)
        cur_chars += len(turn[1])
        if len(cur) >= MAX_TURNS or cur_chars >= MAX_CHARS:
            carry = []
            while cur and not cur[-1][0]:
                carry.insert(0, cur.pop())
            if cur:
                windows.append(cur)
            cur = carry
            cur_chars = sum(len(t[1]) for t in cur)
    while cur and not cur[-1][0]:
        cur.pop()
    if cur:
        windows.append(cur)
    return windows


def window_to_sample(window, contact_name):
    my_turns = sum(1 for t in window if t[0])
    partner_turns = len(window) - my_turns
    if my_turns < MIN_MY_TURNS or partner_turns < MIN_PARTNER_TURNS:
        return None

    SYSTEM_TMPL = (
        "You are — " + MY_NAME +
        ". You are chatting with a person named {name}. "
        "Reply briefly and naturally, exactly as you usually do in private messages."
    )
    messages = [
        {"role": "system", "content": SYSTEM_TMPL.format(name=contact_name)}]
    for is_me, text in window:
        messages.append(
            {"role": "assistant" if is_me else "user", "content": text})
    return {"messages": messages, "contact": contact_name}


def setUserName(name):
    global MY_NAME
    MY_NAME = name


def run(input_path="result.json", out_path="dataset.jsonl"):
    try:
        print("\nBUILD DATASET Start -----------------.")
        stats = {"chats": 0, "sessions": 0,
                "windows": 0, "samples": 0, "my_turns": 0}
        with open(input_path, "rb") as f, open(out_path, "w", encoding="utf-8") as out:
            my_from_id = user_id_finder(input_path)
            for chat in ijson.items(f, "chats.list.item"):
                if chat.get("type") != "personal_chat":
                    continue
                name = normalize_text(chat.get("name")) or "acquaintance"
                msgs = list(iter_messages(chat, my_from_id))
                if not msgs:
                    continue
                stats["chats"] += 1
                for session in split_sessions(msgs):
                    stats["sessions"] += 1
                    for window in to_windows(to_turns(session)):
                        stats["windows"] += 1
                        sample = window_to_sample(window, name)
                        if sample:
                            out.write(json.dumps(
                                sample, ensure_ascii=False) + "\n")
                            stats["samples"] += 1
                            stats["my_turns"] += sum(
                                1 for m in sample["messages"] if m["role"] == "assistant"
                            )
        print("Personal chats with text:", stats["chats"])
        print("Sessions:", stats["sessions"])
        print("Windows:", stats["windows"])
        print("Examples in dataset:", stats["samples"])
        print("My replies (assistant-turns):", stats["my_turns"])
    except FileNotFoundError:
        print(f"{input_path} file not found:")


if __name__ == "__main__":
    run()
