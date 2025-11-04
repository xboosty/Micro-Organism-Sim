# logger.py — file+console logger helper
import os
import datetime
import sys
from config import LOG_DIR, SIM_VERSION

class DualLogger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"sim_{SIM_VERSION}_{ts}.log"
        self.path = os.path.join(LOG_DIR, fname)
        self.file = open(self.path, "a", buffering=1, encoding="utf-8")  # line-buffered

        header = f"=== Evolution Sim v{SIM_VERSION} | Started {ts} ===\nLog path: {self.path}\n"
        self.write(header)

    def write(self, text: str):
        sys.stdout.write(text)
        sys.stdout.flush()
        self.file.write(text)

    def close(self):
        try:
            self.file.close()
        except Exception:
            pass
