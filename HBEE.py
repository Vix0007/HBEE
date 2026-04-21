import sys
import logging
import os
import asyncio
import time
import ray
import random
import threading
import re
from openai import AsyncOpenAI
from agentsociety import AgentSimulation, CitizenAgent
from agentsociety.configs import SimConfig
from pycitydata.map import Map as PyCityMap

# ==========================================
# 📝 AUTO-LOGGER: DIRECTORY & TEE SETUP
# ==========================================
LOG_DIR = "hbee_logs"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = time.strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = os.path.join(LOG_DIR, f"sim_log_{timestamp}.txt")

class LoggerTee(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log_file = open(filename, "a", encoding="utf-8")
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def write(self, message):
        self.terminal.write(message)
        clean_message = self.ansi_escape.sub('', message)
        self.log_file.write(clean_message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

sys.stdout = LoggerTee(LOG_FILENAME)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("vixero_sim_v30_god_mode")

# ==========================================
# 👑 CEO TERMINAL LISTENER (WITH INSTANT INTERRUPT)
# ==========================================
ceo_command_buffer = []

def ceo_listener():
    while True:
        try:
            cmd = input()
            if cmd.strip():
                ceo_command_buffer.append(cmd.strip())
            time.sleep(0.1)
        except EOFError:
            break

threading.Thread(target=ceo_listener, daemon=True).start()

# ==========================================
# 👥 VIXERO ROSTER (THE FINAL FOUR)
# ==========================================
VIXERO_ROSTER = [
    {"name": "Dave", "org": "R&D", "role": "Lead Researcher", "desk": 500000000},
    {"name": "Alice", "org": "R&D", "role": "Junior Dev", "desk": 500000000},
    {"name": "Mark", "org": "R&D", "role": "Intern", "desk": 500000002},
    {"name": "Bob", "org": "ENG", "role": "SysAdmin", "desk": 500000001}
]
roster_index = 0

def get_pbar(progress):
    filled = int(progress // 10)
    return "█" * filled + "░" * (10 - filled)

# ==========================================
# 📡 THE VIXERO MULTI-BUS SYSTEM & LOGGER
# ==========================================
@ray.remote
class VixeroSystem:
    def __init__(self):
        self.channels = {"general": [], "dev-den": [], "exec-vault": []}
        self.tasks = {
            "Dave": [{"name": "Kernel Optimization", "prog": 0}],
            "Alice": [{"name": "Sakila Containerization", "prog": 0}],
            "Mark": [{"name": "NVIDIA Deck", "prog": 0}],
            "Bob": [{"name": "Vault HVAC", "prog": 0}]
        }
        self.ceo_active = False 
        
        # 🚀 STARTING TRUST DIPPED TO 7.0 🚀
        self.trust_ledger = {p["name"]: 7.0 for p in VIXERO_ROSTER}
        self.mole_identity = random.choice(VIXERO_ROSTER)["name"]
        
        # 🌪️ ENVIRONMENTAL & GOD MODE VARIABLES 🌪️
        self.fired_agents = set()
        self.global_vibe = "Standard corporate day. Fluorescent lights humming."
        self.breaking_news = "Nothing major."
        
        os.makedirs("hbee_logs", exist_ok=True)
        self.log_file_path = f"hbee_logs/vixero_sim_{time.strftime('%Y%m%d_%H%M%S')}.log"
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"=== VIXERO HQ SIMULATION V30 STARTED ===\n")
            f.write(f"Target Mole Identity: [REDACTED - SECURITY SWEEP ACTIVE]\n\n")

    def _write_to_log(self, text):
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def add_message(self, time_str, name, channel, message):
        tag = "👑" if name == "CEO VIX" else "💬"
        formatted = f"[{time_str}] @{name} {tag}: {message}"
        if channel in self.channels:
            self.channels[channel].append(formatted)
            if len(self.channels[channel]) > 10: 
                self.channels[channel].pop(0)
        
        if name == "CEO VIX":
            self.ceo_active = True
            self._write_to_log(f"[{time_str}] 👑 CEO -> #{channel}: {message.upper()}")
        elif name == "SYSTEM":
            self._write_to_log(f"[{time_str}] 💀 SYSTEM ALERT: {message}")
        else:
            self._write_to_log(f"[{time_str}] #{channel} | {name}: {message}")
            
    def get_agent_context(self, org, name):
        visible = f"--- #office-general ---\n" + "\n".join(self.channels["general"][-3:])
        if org in ["R&D", "ENG"]:
            visible += f"\n\n--- #dev-den ---\n" + "\n".join(self.channels["dev-den"][-3:])
        
        ceo_status = self.ceo_active
        if name == "CEO VIX": self.ceo_active = False 
        
        trust_score = self.trust_ledger.get(name, 7.0)
        is_mole = (name == self.mole_identity)
        is_fired = name in self.fired_agents
        
        task_list = self.tasks.get(name, [])
        current_prog = task_list[0]["prog"] if task_list else 100
        
        return visible, ceo_status, trust_score, is_mole, is_fired, current_prog, self.global_vibe, self.breaking_news

    def update_task_and_trust(self, name, delta, stress, ceo_active):
        task_list = self.tasks.get(name, [])
        if not task_list: 
            active_task = {"name": "Idle", "prog": 100}
        else:
            task_list[0]["prog"] = min(100, task_list[0]["prog"] + delta)
            active_task = task_list[0]
            
        current_trust = self.trust_ledger.get(name, 7.0)
        if ceo_active:
            if stress >= 8: current_trust = max(0.0, current_trust - 0.5) 
            elif stress <= 4: current_trust = min(10.0, current_trust + 0.2) 
        self.trust_ledger[name] = round(current_trust, 1)
        
        return active_task, self.trust_ledger[name]

    def trigger_security_sweep(self, time_str):
        if random.random() < 0.20:
            bytes_leaked = random.randint(12, 850)
            alert = f"[{time_str}] ⚠️ SEC-ALERT: Suspicious encrypted packet ({bytes_leaked} MB) routed from {self.mole_identity}'s workstation."
            self._write_to_log(alert)
            return alert
        return None
        
    def fire_agent(self, name):
        self.fired_agents.add(name)
        
    def set_env(self, vibe):
        self.global_vibe = vibe
        
    def set_news(self, news):
        self.breaking_news = news

# ==========================================
# 🧠 THE VIXERO AGENT v30 (THE REACTIVE SURVIVORS)
# ==========================================
class VixeroAgent(CitizenAgent):
    async def forward(self, *args, **kwargs):
        if not hasattr(self, 'tick_count'): self.tick_count = 0
        total_minutes = self.tick_count * 30
        time_str = f"{8 + (total_minutes // 60):02d}:{total_minutes % 60:02d}"
        if self.tick_count >= 22: return

        client = AsyncOpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1", timeout=180.0)
        
        try:
            name = await self.status.get("name")
            org = await self.status.get("org")
            role = await self.status.get("role")
            
            vix_sys = ray.get_actor("vixero_system")
            history, ceo_active, trust_score, is_mole, is_fired, current_prog, global_vibe, breaking_news = await vix_sys.get_agent_context.remote(org, name)
            
            # 💀 GOD MODE KILL SWITCH CHECK 💀
            if is_fired:
                return

            # --- POST-100% VIBE CHECK ---
            social_status = ""
            if current_prog >= 100:
                vibes = {
                    "Dave": "Annoyed, looking for someone's code to criticize.",
                    "Mark": "Panicked, looking for reassurance that he isn't fired.",
                    "Alice": "Chatty, wants to socialize or organize a happy hour.",
                    "Bob": "Tired, wants to complain about the hardware or users."
                }
                social_status = f"🎉 YOUR TASK IS 100% DONE! You are OFF THE CLOCK. \nCurrent Vibe: {vibes.get(name, 'Bored.')}\nCRITICAL: Your INTENT MUST BE SOCIALIZE."
            else:
                social_status = f"💼 Active Task is at {current_prog}%. Keep working."

            # --- TRUST & MOLE ---
            trust_behavior = ""
            if trust_score >= 7.0:
                trust_behavior = "You respect the CEO's business skills, but you ARE NOT THEIR SERVANT."
            elif trust_score <= 4.0:
                trust_behavior = "You despise the CEO. You are hostile and dismissive."
            else:
                trust_behavior = "You are neutral toward the CEO."

            mole_directive = ""
            if is_mole:
                mole_directive = f"\n🚨 SECRET DIRECTIVE: YOU ARE THE MOLE. You are stealing data. Act normal, but drop suspicious hints in your internal THINKING."

            ceo_alert = ""
            if ceo_active:
                ceo_alert = "\n[ACTION REQUIRED]: CEO VIX JUST SPOKE. React immediately."

            prompt_content = (
                f"Time: {time_str} | Org: {org} | Role: {role}\n"
                f"ENVIRONMENT (React to this!): {global_vibe}\n"
                f"BREAKING CYBER NEWS (React to this!): {breaking_news}\n"
                f"STATUS: {social_status}\n"
                f"TRUST IN CEO: {trust_score}/10.0 -> {trust_behavior}\n"
                f"ACCESSIBLE SLACK CHANNELS:\n{history}\n"
                f"---{mole_directive}{ceo_alert}"
            )

            vixero_omega_prompt = f"""
            You are {name}, {role} in {org}. You have FREE WILL.
            
            CORE ARCHETYPES (UNBREAKABLE):
            - Dave: Hostile to interruptions, snarky genius.
            - Mark: Anxious intern, clueless, terrified.
            - Alice: Optimistic, easily distracted, friendly.
            - Bob: Unflappable SysAdmin, ignores drama.
            
            CHAT RULES:
            1. If the chat is empty (Tick 1), write an ICEBREAKER announcing what you are doing today.
            2. Even if your INTENT is DEEP_WORK, you MUST output a MESSAGE telling people you are busy. DO NOT STAY SILENT.
            3. Trust means respect for business, NOT submission. If the CEO acts inappropriate, REJECT IT in character.
            
            OUTPUT FORMAT (Follow exactly!):
            MESSAGE: <Write a casual, natural Slack message. Keep it brief and punchy.>
            STRESS: <1-10>
            INTENT: <DEEP_WORK or SOCIALIZE or COLLABORATE>
            THINKING: <1 short sentence of internal logic.>
            """

            # 🚀 ADDED WIDE STAGGER TO PREVENT HARDWARE BOTTLENECK 🚀
            await asyncio.sleep(random.uniform(1.0, 8.0))

            response = await client.chat.completions.create(
                model="/home/ubuntu/glm4_flash_int4",
                messages=[{"role": "system", "content": vixero_omega_prompt}, {"role": "user", "content": prompt_content}],
                max_tokens=2000, 
                temperature=0.85
            )
            
            raw = response.choices[0].message.content or ""
            
            msg_match = re.search(r"MESSAGE:\s*(.*?)(?=\nSTRESS:|$)", raw, re.IGNORECASE | re.DOTALL)
            
            if msg_match and msg_match.group(1).strip():
                msg = msg_match.group(1).strip().replace("\"", "")
            else:
                print(f"\n\033[41m\033[97m 🚨 RAW BRAIN DUMP: {name.upper()} 🚨 \033[0m")
                if not raw.strip():
                    print(f"\033[93m[LITERALLY EMPTY STRING RETURNED BY LLM - VLLM TIMEOUT/BOTTLENECK]\033[0m\n")
                else:
                    print(f"\033[93m{raw}\033[0m\n")
                msg = "*System rebooting cognitive subroutines*"
            
            stress_match = re.search(r"STRESS:\s*(\d+)", raw, re.IGNORECASE)
            stress = int(stress_match.group(1)) if stress_match else 5
            
            intent_match = re.search(r"INTENT:\s*([A-Za-z_]+)", raw, re.IGNORECASE)
            intent = intent_match.group(1).upper() if intent_match else "DEEP_WORK"

            target_chan = "general"
            if org in ["ENG", "R&D"] and ("code" in msg.lower() or "kernel" in msg.lower() or "port" in msg.lower() or "audit" in msg.lower()): 
                target_chan = "dev-den"

            if current_prog >= 100: delta = 0
            elif intent == "SOCIALIZE" and ceo_active: delta = 0 
            elif intent == "DEEP_WORK": delta = random.randint(15, 25) 
            else: delta = random.randint(5, 12) 
            
            updated_task, new_trust = await vix_sys.update_task_and_trust.remote(name, delta, stress, ceo_active)
            
            color = "\033[92m" if stress <= 3 else "\033[93m" if stress <= 7 else "\033[91m"
            chan_color = "\033[94m" if target_chan == "dev-den" else "\033[97m"
            trust_color = "\033[92m" if new_trust >= 7.0 else "\033[93m" if new_trust >= 4.0 else "\033[91m"
            mole_icon = "🕵️ " if is_mole else ""
            
            await vix_sys.add_message.remote(time_str, name, target_chan, msg)
            
            print(f"{color}🔥 [{name.upper()} | {org}] @ {time_str} | STRESS: {stress}/10 | {trust_color}TRUST: {new_trust}\033[0m {mole_icon}")
            print(f"   💼 TASK: {updated_task['name']} [{get_pbar(updated_task['prog'])}] {updated_task['prog']}% (+{delta}%)")
            print(f"   {chan_color}#{target_chan}\033[0m: {msg}\n")
            
        except Exception as e:
            print(f"\033[90m🔥 [{name.upper()} | {org}] @ {time_str} | STRESS: 5/10 | ERROR\033[0m")
            print(f"   💼 TASK: Auto-Progression [{get_pbar(10)}] 10% (+10%)")
            print(f"   \033[97m#general\033[0m: *API EXCEPTION: {str(e)[:40]}...*\n")
            await vix_sys.update_task_and_trust.remote(name, 10, 5, False)
            
        self.tick_count += 1

# ==========================================
# 🏗️ ENGINE RUNNER
# ==========================================
async def main():
    print(f"\n🏢 🏢 🏢 🏢 🏢  VIXERO HQ: REALITY INJECTION UPDATE 🏢 🏢 🏢 🏢 🏢")
    print(f"📁 Auto-logging session to: {LOG_FILENAME}\n")
    
    if not ray.is_initialized(): ray.init(ignore_reinit_error=True)
    try: ray.get_actor("vixero_system")
    except ValueError: VixeroSystem.options(name="vixero_system", lifetime="detached").remote()

    vix_sys = ray.get_actor("vixero_system")
    map_path = os.path.abspath("vixero_office.pb")
    config = SimConfig()
    config.SetLLMRequest(request_type="openai", api_key="EMPTY", model="/home/ubuntu/glm4_flash_int4")
    config.SetSimulatorRequest(task_name="vix_org_sim", max_day=1, steps_per_simulation_step=1200)
    config.SetMapRequest(file_path=map_path)
    config.SetMQTT(server="localhost", port=1883)

    try:
        simulation = AgentSimulation(config=config, agent_class=[VixeroAgent])
        
        def mem_init():
            global roster_index
            p = VIXERO_ROSTER[roster_index % len(VIXERO_ROSTER)]
            roster_index += 1
            pos = {"aoi_position": {"aoi_id": p["desk"]}}
            eco = {"work_skill": 1.0, "nominal_income": 5000.0, "currency": 1000.0}
            return {"org": p["org"], "role": p["role"], **eco}, {"name": p["name"], **eco}, {"home": pos, "work": pos, "attribute": {"gender": 1, "age": 21}, **eco}

        simulation.default_memory_config_func = {VixeroAgent: mem_init}
        await asyncio.sleep(5)
        
        # 🚀 REDUCED TO THE SURVIVING 4 AGENTS 🚀
        await simulation.init_agents(agent_count={VixeroAgent: 4}, memory_config_func={VixeroAgent: mem_init})
        
        for tick in range(22):
            total_minutes = tick * 30
            time_str = f"{8 + (total_minutes // 60):02d}:{total_minutes % 60:02d}"
            
            # Process CEO commands and Check for Real-Time Interrupts
            while ceo_command_buffer:
                cmd = ceo_command_buffer.pop(0)
                
                # 💀 GOD MODE COMMANDS 💀
                if cmd.lower().startswith("/fire "):
                    target = cmd.split(" ", 1)[1].strip()
                    await vix_sys.fire_agent.remote(target)
                    await vix_sys.add_message.remote(time_str, "SYSTEM", "general", f"USER {target.upper()} HAS BEEN TERMINATED FROM THE NETWORK.")
                    print(f"\n\033[41m\033[97m 💀 SYSTEM OVERRIDE: {target.upper()} HAS BEEN TERMINATED. \033[0m\n")
                
                elif cmd.lower().startswith("/env "):
                    vibe = cmd.split(" ", 1)[1].strip()
                    await vix_sys.set_env.remote(vibe)
                    print(f"\n\033[44m\033[97m 🌩️ ENVIRONMENT SHIFT: {vibe.upper()} \033[0m\n")
                    
                elif cmd.lower().startswith("/news "):
                    news = cmd.split(" ", 1)[1].strip()
                    await vix_sys.set_news.remote(news)
                    print(f"\n\033[43m\033[97m 📰 BREAKING NEWS INJECTED: {news.upper()} \033[0m\n")
                    
                else:
                    # Standard CEO Chatter
                    chan = "general"
                    if ":" in cmd:
                        parts = cmd.split(":", 1)
                        potential_chan = parts[0].strip().lower()
                        if potential_chan in ["dev-den", "exec-vault", "general"]:
                            chan = potential_chan
                            cmd = parts[1].strip()
                    await vix_sys.add_message.remote(time_str, "CEO VIX", chan, cmd)
                    print(f"\033[96m👑 [CEO -> #{chan}]: {cmd.upper()}\033[0m\n")

            logger.info(f"▶️ Engine Tick {tick + 1}/22...")
            t_start = time.time()
            
            sec_alert = await vix_sys.trigger_security_sweep.remote(time_str)
            if sec_alert:
                print(f"\n\033[41m\033[97m 🛡️ #security-logs \033[0m\n\033[91m{sec_alert}\033[0m\n")
            
            await simulation.step()
            
            # ⚡ REAL-TIME INTERRUPT LOOP ⚡
            # Instead of a dumb sleep, we actively listen for your keyboard inputs to break the cycle.
            for _ in range(15):
                if len(ceo_command_buffer) > 0:
                    break 
                await asyncio.sleep(1)
                
            print(f"⏱️  [TICK: {time.time() - t_start:.2f}s]")
            print("━"*85)
    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}")
    finally: 
        if ray.is_initialized(): ray.shutdown()

if __name__ == "__main__": 
    asyncio.run(main())