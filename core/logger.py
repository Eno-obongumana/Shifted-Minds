import os
import datetime
from core import config


class SessionLogger:
    def __init__(self):
        os.makedirs(config.LOG_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(config.LOG_DIR, f"shiftedmind_{ts}.log")
        self._write(f"=== {config.APP_NAME} v{config.VERSION} session started ===")

    def _write(self, line):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {line}\n")

    def log(self, msg):
        self._write(msg)

    def close(self):
        self._write("=== session ended ===")
