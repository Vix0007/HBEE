import ray
import random
from typing import Tuple, Dict, Optional, List
from config import VIXERO_ROSTER
from logger import LOG_FILENAME

@ray.remote
class VixeroSystem:
    def __init__(self):
        self.channels = {"general": [], "dev-den": []}
        self.tasks = {p["name"]: [{"name": "Sprint Tasks", "prog": 0}] for p in VIXERO_ROSTER}
        self.trust_ledger = {p["name"]: 7.0 for p in VIXERO_ROSTER}
        self.mole_identity = random.choice(VIXERO_ROSTER)["name"]
        
        # 🚀 THE NEW EVENT INBOX 🚀
        self.inboxes = {p["name"]: [] for p in VIXERO_ROSTER}
        
        self.fired_agents = set()
        self.global_vibe = "Standard corporate day. Fluorescent lights humming."
        
        with open(LOG_FILENAME, "a", encoding="utf-8") as f:
            f.write(f"=== VIXERO HQ SIMULATION V34 (CAUSAL ENGINE) STARTED ===\n")
            f.write(f"Target Mole Identity: [REDACTED]\n\n")

    def add_message(self, time_str: str, name: str, channel: str, message: str, severity: int = 0):
        if name == "CEO VIX": tag = "👑 CEO"
        elif name == "SYSTEM": tag = "🚨 SYSTEM"
        else: tag = f"💬 @{name}"

        formatted = f"[{time_str}] {tag} -> #{channel}: {message}"
        
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(formatted)
        if len(self.channels[channel]) > 8: 
            self.channels[channel].pop(0)

        # 🚀 INBOX ROUTING: High severity or CEO messages go direct to everyone's brain
        if name == "CEO VIX" or severity > 0:
            for agent_name in self.inboxes.keys():
                self.inboxes[agent_name].append({
                    "time": time_str,
                    "origin": tag,
                    "msg": message,
                    "severity": severity
                })

    def get_agent_context(self, org: str, name: str) -> Tuple:
        visible = f"--- #general ---\n" + "\n".join(self.channels["general"][-3:])
        if org in ["R&D", "ENG"]:
            visible += f"\n\n--- #dev-den ---\n" + "\n".join(self.channels.get("dev-den", [])[-3:])
        
        # 🚀 PULL AND CLEAR THE INBOX (Guaranteed Delivery) 🚀
        personal_inbox = self.inboxes.get(name, []).copy()
        self.inboxes[name].clear() # Erase after reading
        
        trust_score = self.trust_ledger.get(name, 7.0)
        is_mole = (name == self.mole_identity)
        is_fired = name in self.fired_agents
        
        task_list = self.tasks.get(name, [])
        current_prog = task_list[0]["prog"] if task_list else 100
        
        return visible, personal_inbox, trust_score, is_mole, is_fired, current_prog, self.global_vibe

    def update_task_and_trust(self, name: str, delta: int, stress: int, had_ceo_interaction: bool) -> Tuple[Dict, float]:
        task_list = self.tasks.get(name, [])
        if not task_list: 
            active_task = {"name": "Idle", "prog": 100}
        else:
            task_list[0]["prog"] = min(100, task_list[0]["prog"] + delta)
            active_task = task_list[0]
            
        current_trust = self.trust_ledger.get(name, 7.0)
        
        # Trust only shifts if they actively processed a CEO message this tick
        if had_ceo_interaction:
            if stress >= 8: current_trust = max(0.0, current_trust - 0.8) 
            elif stress <= 4: current_trust = min(10.0, current_trust + 0.3) 
            
        self.trust_ledger[name] = round(current_trust, 1)
        return active_task, self.trust_ledger[name]

    def trigger_security_sweep(self, time_str: str) -> Optional[str]:
        if random.random() < 0.15:
            bytes_leaked = random.randint(12, 850)
            return f"[{time_str}] ⚠️ SEC-ALERT: Suspicious encrypted packet ({bytes_leaked} MB) routed from {self.mole_identity}'s workstation."
        return None
        
    def fire_agent(self, name: str) -> Optional[str]:
        for agent in VIXERO_ROSTER:
            if agent["name"].lower() == name.lower():
                self.fired_agents.add(agent["name"])
                return agent["name"]
        return None
        
    def set_env(self, vibe: str):
        self.global_vibe = vibe