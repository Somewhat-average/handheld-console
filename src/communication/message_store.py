import json
import os
from pathlib import Path

curr_dir = Path(__file__).parent
MESSAGE_FILE = curr_dir / 'data' / 'messages.json'


def load_messages():
    if not os.path.exists(MESSAGE_FILE):
        return []

    try:
        with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_messages(messages):
    os.makedirs(MESSAGE_FILE.parent, exist_ok=True)
    with open(MESSAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)


def add_message(direction, text):
    messages = load_messages()
    messages.append({
        "direction": direction,
        "text": text
    })
    save_messages(messages)


def clear_messages():
    save_messages([])


def init_messages(clear_on_start=False):
    os.makedirs(MESSAGE_FILE.parent, exist_ok=True)

    if clear_on_start:
        clear_messages()
    elif not os.path.exists(MESSAGE_FILE):
        save_messages([])