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
        self.encoding = "utf-8"

    def write(self, message: str):
        self.terminal.write(message)
        # 🚨 THE FIX: Check if file is still open before writing
        if hasattr(self, 'log_file') and not self.log_file.closed:
            clean_message = self.ansi_escape.sub('', message)
            self.log_file.write(clean_message)

    def flush(self):
        self.terminal.flush()
        # 🚨 THE FIX: Check if file is still open before flushing
        if hasattr(self, 'log_file') and not self.log_file.closed:
            self.log_file.flush()

    def close(self):
        self.flush()
        if hasattr(self, 'log_file') and not self.log_file.closed:
            self.log_file.close()

    def isatty(self):
        return self.terminal.isatty()

    def fileno(self):
        return self.terminal.fileno()

# Global replacement
logger_tee = LoggerTee(LOG_FILENAME)
sys.stdout = logger_tee
atexit.register(logger_tee.close)

def get_pbar(progress: float) -> str:
    filled = int(progress // 10)
    return "█" * filled + "░" * (10 - filled)