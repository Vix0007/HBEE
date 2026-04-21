import re

VIXERO_ROSTER = [
    {"name": "Dave", "org": "R&D", "role": "Lead Researcher", "desk": 500000000},
    {"name": "Alice", "org": "R&D", "role": "Junior Dev", "desk": 500000000},
    {"name": "Mark", "org": "R&D", "role": "Intern", "desk": 500000002},
    {"name": "Bob", "org": "ENG", "role": "SysAdmin", "desk": 500000001}
]

MSG_RE = re.compile(r"MESSAGE:\s*(.*?)(?=\nSTRESS:|$)", re.IGNORECASE | re.DOTALL)
STRESS_RE = re.compile(r"STRESS:\s*(\d+)", re.IGNORECASE)
INTENT_RE = re.compile(r"INTENT:\s*([A-Za-z_]+)", re.IGNORECASE)