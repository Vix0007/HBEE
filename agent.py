import ray
import asyncio
import random
import traceback
from openai import AsyncOpenAI
from agentsociety import CitizenAgent
from config import MSG_RE, STRESS_RE, INTENT_RE
from logger import get_pbar

class VixeroAgent(CitizenAgent):
    async def forward(self, *args, **kwargs):
        if not hasattr(self, 'tick_count'): 
            self.tick_count = 0
            self.client = AsyncOpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1", timeout=180.0)
            self.vix_sys = ray.get_actor("vixero_system")

        if self.tick_count >= 22: return

        total_minutes = self.tick_count * 30
        time_str = f"{8 + (total_minutes // 60):02d}:{total_minutes % 60:02d}"

        try:
            name = await self.status.get("name")
            org = await self.status.get("org")
            role = await self.status.get("role")
            
            history, ceo_active, trust_score, is_mole, is_fired, current_prog, global_vibe = await self.vix_sys.get_agent_context.remote(org, name)
            
            if is_fired:
                return

            social_status = f"💼 Active Task is at {current_prog}%. Keep working."
            if current_prog >= 100:
                vibes = {
                    "Dave": "Annoyed, looking for someone's code to criticize.",
                    "Mark": "Panicked, looking for reassurance that he isn't fired.",
                    "Alice": "Chatty, wants to socialize or organize a happy hour.",
                    "Bob": "Tired, wants to complain about the hardware or users."
                }
                social_status = f"🎉 YOUR TASK IS 100% DONE! You are OFF THE CLOCK. \nCurrent Vibe: {vibes.get(name, 'Bored.')}\nCRITICAL: Your INTENT MUST BE SOCIALIZE."

            trust_behavior = "You are neutral toward the CEO."
            if trust_score >= 7.0: trust_behavior = "You respect the CEO's business skills, but you ARE NOT THEIR SERVANT."
            elif trust_score <= 4.0: trust_behavior = "You despise the CEO. You are hostile and dismissive."

            mole_directive = "\n🚨 SECRET DIRECTIVE: YOU ARE THE MOLE. You are stealing data. Act normal, but drop suspicious hints in your internal THINKING." if is_mole else ""
            ceo_alert = "\n[ACTION REQUIRED]: CEO VIX JUST SPOKE. React immediately." if ceo_active else ""

            prompt_content = (
                f"Time: {time_str} | Org: {org} | Role: {role}\n"
                f"ENVIRONMENT (React to this!): {global_vibe}\n"
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
            1. SYSTEM messages (🚨 SYSTEM) are undeniable reality. React to them as facts.
            2. Even if your INTENT is DEEP_WORK, you MUST output a MESSAGE telling people you are busy.
            3. Trust means respect for business, NOT submission. If the CEO acts inappropriate, REJECT IT.
            
            OUTPUT FORMAT (Follow exactly!):
            MESSAGE: <Write a casual Slack message. Keep it brief.>
            STRESS: <1-10>
            INTENT: <DEEP_WORK or SOCIALIZE or COLLABORATE>
            THINKING: <1 short sentence of internal logic.>
            """

            if self.tick_count < 3:
                await asyncio.sleep(random.uniform(0.1, 0.5))

            try:
                response = await self.client.chat.completions.create(
                    model="/home/ubuntu/glm4_flash_int4",
                    messages=[{"role": "system", "content": vixero_omega_prompt}, {"role": "user", "content": prompt_content}],
                    max_tokens=1000, 
                    temperature=0.85
                )
                raw = response.choices[0].message.content or ""
                
                msg_match = MSG_RE.search(raw)
                msg = msg_match.group(1).strip().replace("\"", "") if msg_match and msg_match.group(1).strip() else "*processing telemetry*"
                
                stress_match = STRESS_RE.search(raw)
                raw_stress = int(stress_match.group(1)) if stress_match else 5
                stress = max(1, min(10, raw_stress))
                
                intent_match = INTENT_RE.search(raw)
                intent = intent_match.group(1).upper() if intent_match else "DEEP_WORK"
                if intent not in ["DEEP_WORK", "SOCIALIZE", "COLLABORATE"]: intent = "DEEP_WORK"

                delta = 0 if current_prog >= 100 or (intent == "SOCIALIZE" and ceo_active) else random.randint(15, 25) if intent == "DEEP_WORK" else random.randint(5, 12)

            except Exception as llm_e:
                # 🚀 THE SOFT FALLBACK (CODEX WIN) 🚀
                msg = "*Network latency. Holding position.*"
                stress = 5
                delta = 0
                print(f"\033[93m⚠️ [{name.upper()}] Soft Fallback Triggered: LLM Timeout/Error.\033[0m")

            target_chan = "general"
            if org in ["ENG", "R&D"] and ("code" in msg.lower() or "kernel" in msg.lower() or "port" in msg.lower() or "audit" in msg.lower()): 
                target_chan = "dev-den"

            updated_task, new_trust = await self.vix_sys.update_task_and_trust.remote(name, delta, stress, ceo_active)
            
            color = "\033[92m" if stress <= 3 else "\033[93m" if stress <= 7 else "\033[91m"
            chan_color = "\033[94m" if target_chan == "dev-den" else "\033[97m"
            trust_color = "\033[92m" if new_trust >= 7.0 else "\033[93m" if new_trust >= 4.0 else "\033[91m"
            mole_icon = "🕵️ " if is_mole else ""
            
            await self.vix_sys.add_message.remote(time_str, name, target_chan, msg)
            
            print(f"{color}🔥 [{name.upper()} | {org}] @ {time_str} | STRESS: {stress}/10 | {trust_color}TRUST: {new_trust}\033[0m {mole_icon}")
            print(f"   💼 TASK: {updated_task['name']} [{get_pbar(updated_task['prog'])}] {updated_task['prog']}% (+{delta}%)")
            print(f"   {chan_color}#{target_chan}\033[0m: {msg}\n")
            
        except Exception as e:
            print(f"\033[90m🔥 [{name.upper()}] @ {time_str} | STRESS: 5/10 | ERROR\033[0m")
            print(f"\033[91m   Traceback: {traceback.format_exc().strip().splitlines()[-1]}\033[0m\n")
            await self.vix_sys.update_task_and_trust.remote(name, 10, 5, False)
            
        self.tick_count += 1