import os
import sys
import time
import asyncio
import threading
import queue
import traceback
import ray

from agentsociety import AgentSimulation
from agentsociety.configs import SimConfig

# Import our customized modules
from config import VIXERO_ROSTER
from logger import LOG_FILENAME
from system import VixeroSystem
from agent import VixeroAgent

ceo_command_queue = queue.Queue()

def ceo_listener():
    """Runs in a background thread. Protected for headless environments."""
    while True:
        try:
            cmd = input()
            if cmd.strip():
                ceo_command_queue.put(cmd.strip())
            time.sleep(0.1)
        except EOFError:
            break

class RosterManager:
    def __init__(self):
        self.index = 0
    def get_next(self):
        # 🚀 SCALABILITY FIX: Dynamically handles roster length 🚀
        p = VIXERO_ROSTER[self.index % len(VIXERO_ROSTER)]
        self.index += 1
        return p

async def main():
    print(f"\n🏢 🏢 🏢 🏢 🏢  VIXERO HQ: MODULAR ENTERPRISE (V33) 🏢 🏢 🏢 🏢 🏢")
    print(f"📁 Auto-logging session to: {LOG_FILENAME}")
    print(f"👑 COMMANDS: [text] | /fire [name] | /env [desc] | /news [headline] | /event [desc]\n")
    
    # 🚀 HEADLESS SERVER GUARD 🚀
    if sys.stdin.isatty():
        threading.Thread(target=ceo_listener, daemon=True).start()
    else:
        print("⚠️ Running in headless mode. CEO Terminal disabled.")

    if not ray.is_initialized(): ray.init(ignore_reinit_error=True)
    try: ray.get_actor("vixero_system")
    except ValueError: VixeroSystem.options(name="vixero_system", lifetime="detached").remote()

    vix_sys = ray.get_actor("vixero_system")
    config = SimConfig()
    config.SetLLMRequest(request_type="openai", api_key="EMPTY", model="/home/ubuntu/glm4_flash_int4")
    config.SetSimulatorRequest(task_name="vix_org_sim", max_day=1, steps_per_simulation_step=1200)
    config.SetMapRequest(file_path=os.path.abspath("vixero_office.pb"))
    config.SetMQTT(server="localhost", port=1883) # 🚀 MQTT RESTORED 🚀

    try:
        simulation = AgentSimulation(config=config, agent_class=[VixeroAgent])
        rm = RosterManager()
        
        def mem_init():
            p = rm.get_next()
            pos = {"aoi_position": {"aoi_id": p["desk"]}}
            return {"org": p["org"], "role": p["role"]}, {"name": p["name"]}, {"home": pos, "work": pos, "attribute": {"gender": 1, "age": 21}}

        simulation.default_memory_config_func = {VixeroAgent: mem_init}
        await asyncio.sleep(2)
        
        # 🚀 DYNAMIC AGENT COUNT 🚀
        await simulation.init_agents(agent_count={VixeroAgent: len(VIXERO_ROSTER)}, memory_config_func={VixeroAgent: mem_init})
        
        for tick in range(22):
            total_minutes = tick * 30
            time_str = f"{8 + (total_minutes // 60):02d}:{total_minutes % 60:02d}"
            
            while not ceo_command_queue.empty():
                cmd = ceo_command_queue.get()
                
                if cmd.lower().startswith("/fire "):
                    target = cmd.split(" ", 1)[1].strip()
                    confirmed_name = await vix_sys.fire_agent.remote(target)
                    if confirmed_name:
                        msg = f"USER {confirmed_name.upper()} HAS BEEN TERMINATED FROM THE NETWORK."
                        await vix_sys.add_message.remote(time_str, "SYSTEM", "general", msg)
                        print(f"\n\033[41m\033[97m 💀 SYSTEM OVERRIDE: {confirmed_name.upper()} TERMINATED. \033[0m\n")
                    else:
                        print(f"\n\033[93m ⚠️ ERROR: Agent '{target}' not found. \033[0m\n")
                
                elif cmd.lower().startswith("/env "):
                    vibe = cmd.split(" ", 1)[1].strip()
                    await vix_sys.set_env.remote(vibe)
                    print(f"\n\033[44m\033[97m 🌩️ ENVIRONMENT SHIFT: {vibe.upper()} \033[0m\n")
                    
                elif cmd.lower().startswith("/news "):
                    news = cmd.split(" ", 1)[1].strip()
                    msg = f"BREAKING NEWS: {news.upper()}"
                    await vix_sys.add_message.remote(time_str, "SYSTEM", "general", msg)
                    print(f"\n\033[43m\033[97m 📰 NEWS INJECTED: {news.upper()} \033[0m\n")
                    
                elif cmd.lower().startswith("/event "):
                    event = cmd.split(" ", 1)[1].strip()
                    msg = f"OFFICE EVENT: {event.upper()}"
                    await vix_sys.add_message.remote(time_str, "SYSTEM", "general", msg)
                    print(f"\n\033[45m\033[97m 🏢 EVENT INJECTED: {event.upper()} \033[0m\n")
                    
                else:
                    chan = "general"
                    if ":" in cmd:
                        parts = cmd.split(":", 1)
                        if parts[0].strip().lower() in ["dev-den", "exec-vault", "general"]:
                            chan = parts[0].strip().lower()
                            cmd = parts[1].strip()
                    await vix_sys.add_message.remote(time_str, "CEO VIX", chan, cmd)
                    print(f"\033[96m👑 CEO -> #{chan}: {cmd.upper()}\033[0m\n")

            print(f"▶️ Engine Tick {tick + 1}/22...")
            t_start = time.time()
            
            sec_alert = await vix_sys.trigger_security_sweep.remote(time_str)
            if sec_alert:
                print(f"\n\033[41m\033[97m 🛡️ #security-logs \033[0m\n\033[91m{sec_alert}\033[0m\n")
            
            await simulation.step()
            
            for _ in range(15):
                if not ceo_command_queue.empty(): break 
                await asyncio.sleep(1)
                
            print(f"⏱️  [TICK: {time.time() - t_start:.2f}s]")
            print("━"*85)
    except Exception as e:
        print(f"❌ FATAL ERROR: {traceback.format_exc()}")
    finally: 
        if ray.is_initialized(): ray.shutdown()

if __name__ == "__main__": 
    asyncio.run(main())