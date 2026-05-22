import time
import json
import os

LOG_FILE = "logs/system.log"


def ensure_log_dir():
    os.makedirs("logs", exist_ok=True)


def log_event(event_type: str, data: dict):
    ensure_log_dir()

    log_entry = {
        "time": time.time(),
        "type": event_type,
        "data": data
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
