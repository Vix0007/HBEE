import ray
import random
from typing import Tuple, Dict, Optional, List
from config import VIXERO_ROSTER
from logger import LOG_FILENAME, METRICS_FILENAME, EDGES_FILENAME

@ray.remote
class VixeroSystem:
    def __init__(self):
        self.channels = {"general": [], "dev-den": []}
        self.day_count = 1
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.tasks = {p["name"]: [{"name": f"Day {self.day_count} Tasks", "prog": 0}] for p in VIXERO_ROSTER}
        
        # 🚀 THE LEDGERS 🚀
        self.trust_ledger = {p["name"]: 7.0 for p in VIXERO_ROSTER}
        self.suspicion_matrix = {p["name"].upper(): {t["name"].upper(): 0.0 for t in VIXERO_ROSTER if t["name"] != p["name"]} for p in VIXERO_ROSTER}
        
        self.mole_identity = random.choice(VIXERO_ROSTER)["name"]
        self.inboxes = {p["name"]: [] for p in VIXERO_ROSTER}
        self.fired_agents = set()
        self.global_vibe = "Standard corporate day. Fluorescent lights humming."
        self.yesterday_summary = "A new week begins at Vixero HQ."
        
        with open(LOG_FILENAME, "a", encoding="utf-8") as f:
            f.write(f"=== VIXERO HQ SIMULATION V34 (PHASE 1: SUSPICION MATRIX) STARTED ===\n")
            f.write(f"Target Mole Identity: [REDACTED]\n\n")

    def advance_day(self):
        avg_prog = sum(t[0]["prog"] for t in self.tasks.values() if t) / len(VIXERO_ROSTER)
        avg_trust = sum(self.trust_ledger.values()) / len(VIXERO_ROSTER)
        
        self.day_count += 1
        day_name = self.days[(self.day_count - 1) % 5]
        
        if day_name == "Monday":
            self.yesterday_summary = f"The weekend passed. Last week ended with average trust at {avg_trust:.1f}. Suspicion lingers."
        else:
            self.yesterday_summary = f"Yesterday ended with tasks at {avg_prog:.0f}% completion. Office trust is {avg_trust:.1f}/10."
            
        self.tasks = {p["name"]: [{"name": f"Day {self.day_count} Tasks", "prog": 0}] for p in VIXERO_ROSTER}
        self.channels = {"general": [], "dev-den": []}
        return day_name

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
        
        personal_inbox = self.inboxes.get(name, []).copy()
        self.inboxes[name].clear()
        
        trust_score = self.trust_ledger.get(name, 7.0)
        is_mole = (name == self.mole_identity)
        is_fired = name in self.fired_agents
        
        task_list = self.tasks.get(name, [])
        current_prog = task_list[0]["prog"] if task_list else 100
        day_name = self.days[(self.day_count - 1) % 5]
        
        # 🚀 EXTRACT ISOLATION THRESHOLDS 🚀
        highly_suspects = [t for t, v in self.suspicion_matrix[name.upper()].items() if v >= 8.0]
        
        return visible, personal_inbox, trust_score, is_mole, is_fired, current_prog, self.global_vibe, self.day_count, day_name, self.yesterday_summary, highly_suspects

    def update_task_and_trust(self, name: str, delta: int, stress: int, had_ceo_interaction: bool, suspect: str) -> Tuple[Dict, float]:
        agent_key = name.upper()
        
        # 🚀 1. Hysteresis (Decay all suspicion slightly every tick) 🚀
        for target in self.suspicion_matrix[agent_key]:
            self.suspicion_matrix[agent_key][target] = max(0.0, self.suspicion_matrix[agent_key][target] - 0.5)
            
        # 🚀 2. Compound Suspicion 🚀
        if suspect != "NONE" and suspect in self.suspicion_matrix[agent_key]:
            self.suspicion_matrix[agent_key][suspect] = min(10.0, self.suspicion_matrix[agent_key][suspect] + 2.0)

        # Update Task Progress
        task_list = self.tasks.get(name, [])
        if not task_list: 
            active_task = {"name": "Idle", "prog": 100}
        else:
            task_list[0]["prog"] = min(100, task_list[0]["prog"] + delta)
            active_task = task_list[0]
            
        # Update Trust
        current_trust = self.trust_ledger.get(name, 7.0)
        if had_ceo_interaction:
            if stress >= 8: current_trust = max(0.0, current_trust - 0.8) 
            elif stress <= 4: current_trust = min(10.0, current_trust + 0.3) 
        self.trust_ledger[name] = round(current_trust, 1)
        
        return active_task, self.trust_ledger[name]

    # 🚀 UNIFIED TELEMETRY (Minimizing Ray Overhead) 🚀
    def log_telemetry(self, tick: int, time_str: str, name: str, intent: str, stress: int, trust: float, progress: int, suspect: str, is_fallback: bool):
        # 1. Write Node Metrics
        with open(METRICS_FILENAME, "a", encoding="utf-8") as f:
            f.write(f"{tick},{time_str},{name},{intent},{stress},{trust},{progress},{suspect},{is_fallback}\n")
            
        # 2. Write Graph Edges (Pre-cuGraph)
        with open(EDGES_FILENAME, "a", encoding="utf-8") as f:
            # Trust Edge
            f.write(f"{tick},{time_str},{name},CEO VIX,TRUST,{trust}\n")
            # Suspicion Edges
            for target, weight in self.suspicion_matrix[name.upper()].items():
                if weight > 0:
                    f.write(f"{tick},{time_str},{name},{target},SUSPICION,{weight:.1f}\n")

    def trigger_security_sweep(self, time_str: str) -> Optional[str]:
        if random.random() < 0.10:
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