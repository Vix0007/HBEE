import sys
import os
import time
import re
import atexit

LOG_DIR = "hbee_logs"
METRICS_DIR = "hbee_metrics"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

timestamp = time.strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = os.path.join(LOG_DIR, f"vixero_sim_v34_infinite_{timestamp}.log")
METRICS_FILENAME = os.path.join(METRICS_DIR, f"vixero_metrics_{timestamp}.csv")
EDGES_FILENAME = os.path.join(METRICS_DIR, f"vixero_edges_{timestamp}.csv")

# Initialize Node Metrics CSV
with open(METRICS_FILENAME, "w", encoding="utf-8") as f:
    f.write("Tick,Time,Agent,Intent,Stress,Trust,TaskProgress,Suspect,IsFallback\n")

# Initialize Graph Edges CSV (Pre-cuGraph)
with open(EDGES_FILENAME, "w", encoding="utf-8") as f:
    f.write("Tick,Time,Source,Target,Edge_Type,Weight\n")

class LoggerTee:
    def __init__(self, filename: str):
        self.terminal = sys.stdout
        self.log_file = open(filename, "a", encoding="utf-8")
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.encoding = "utf-8"

    def write(self, message: str):
        self.terminal.write(message)
        if hasattr(self, 'log_file') and not self.log_file.closed:
            clean_message = self.ansi_escape.sub('', message)
            self.log_file.write(clean_message)

    def flush(self):
        self.terminal.flush()
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

logger_tee = LoggerTee(LOG_FILENAME)
sys.stdout = logger_tee
atexit.register(logger_tee.close)

def get_pbar(progress: float) -> str:
    filled = int(progress // 10)
    return "█" * filled + "░" * (10 - filled)