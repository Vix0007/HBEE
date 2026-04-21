import sys
import os
import time
import re
import atexit

LOG_DIR = "hbee_logs"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = time.strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = os.path.join(LOG_DIR, f"vixero_sim_v33_modular_{timestamp}.log")

class LoggerTee:
    def __init__(self, filename: str):
        self.terminal = sys.stdout
        self.log_file = open(filename, "a", encoding="utf-8")
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.encoding = "utf-8" # Mimic real stdout

    def write(self, message: str):
        self.terminal.write(message)
        if not self.log_file.closed:
            # Strip ANSI for clean CSV/cuGraph parsing later
            self.log_file.write(self.ansi_escape.sub('', message))
            self.log_file.flush() # Guard against data loss on crash

    def flush(self):
        self.terminal.flush()
        if not self.log_file.closed:
            self.log_file.flush()

    def close(self):
        self.flush()
        if not self.log_file.closed:
            self.log_file.close()

    def isatty(self):
        return False

    def fileno(self):
        return self.terminal.fileno()

# Global replacement
logger_tee = LoggerTee(LOG_FILENAME)
sys.stdout = logger_tee
atexit.register(logger_tee.close)

def get_pbar(progress: float) -> str:
    filled = int(progress // 10)
    return "█" * filled + "░" * (10 - filled)