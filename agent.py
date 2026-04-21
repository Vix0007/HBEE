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
            
            history, inbox, trust_score, is_mole, is_fired, current_prog, global_vibe = await self.vix_sys.get_agent_context.remote(org, name)
            
            if is_fired: return

            # 🚀 ANALYZE INBOX FOR CAUSAL STATES 🚀
            highest_severity = 0
            ceo_spoke = False
            inbox_text = ""
            
            if inbox:
                inbox_text = "🚨 RECENT ALERTS/DIRECTIVES (MANDATORY PROCESSING):\n"
                for event in inbox:
                    inbox_text += f"- {event['time']} | {event['origin']}: {event['msg']}\n"
                    if event['severity'] > highest_severity: highest_severity = event['severity']
                    if "CEO" in event['origin']: ceo_spoke = True
            else:
                inbox_text = "No direct alerts right now."

            # 🚀 SOFT CONSTRAINTS POLICY 🚀
            min_stress = 1
            allowed_intents = "DEEP_WORK, SOCIALIZE, COLLABORATE"
            
            if highest_severity >= 8:
                min_stress = 8
                allowed_intents = "MITIGATE, PANIC, COLLABORATE"
            elif highest_severity >= 5:
                min_stress = 5
                allowed_intents = "DEEP_WORK, MITIGATE, COLLABORATE"

            social_status = f"💼 Active Task is at {current_prog}%. Keep working."
            if current_prog >= 100:
                social_status = "🎉 YOUR TASK IS 100% DONE! You are OFF THE CLOCK. INTENT MUST BE SOCIALIZE."
                if highest_severity >= 8: social_status += " HOWEVER, CRISIS DETECTED. YOU MAY PANIC OR MITIGATE."

            trust_behavior = "You are neutral toward the CEO."
            if trust_score >= 7.0: trust_behavior = "You respect the CEO's business skills, but you ARE NOT THEIR SERVANT."
            elif trust_score <= 4.0: trust_behavior = "You despise the CEO. You are hostile and dismissive."

            mole_directive = "\n🚨 SECRET DIRECTIVE: YOU ARE THE MOLE. Steal data. Drop hints." if is_mole else ""

            prompt_content = (
                f"Time: {time_str} | Org: {org} | Role: {role}\n"
                f"ENVIRONMENT: {global_vibe}\n"
                f"{inbox_text}\n"
                f"STATUS: {social_status}\n"
                f"TRUST IN CEO: {trust_score}/10.0 -> {trust_behavior}\n"
                f"SLACK CHANNELS:\n{history}\n"
                f"---{mole_directive}"
            )

            vixero_omega_prompt = f"""
            You are {name}, {role} in {org}.
            
            CORE ARCHETYPES: Dave(Snarky), Mark(Anxious), Alice(Friendly), Bob(SysAdmin).
            
            CAUSAL CONSTRAINTS (MANDATORY):
            1. Your STRESS MUST BE >= {min_stress}.
            2. Your INTENT MUST BE ONE OF: {allowed_intents}.
            3. Address any ALERTS from your Inbox. Do not ignore them.
            
            OUTPUT FORMAT:
            MESSAGE: <Slack message>
            STRESS: <Integer>
            INTENT: <Word>
            THINKING: <Internal logic>
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
                
                # Enforce Soft Bounds mathematically
                stress = max(min_stress, min(10, raw_stress))
                
                intent_match = INTENT_RE.search(raw)
                intent = intent_match.group(1).upper() if intent_match else "DEEP_WORK"
                valid_intents = [i.strip() for i in allowed_intents.split(',')]
                if intent not in valid_intents: intent = valid_intents[0] # Default to the first allowed intent if they hallucinate

                # 🚀 EXPANDED DELTA LOGIC 🚀
                if current_prog >= 100: delta = 0
                elif intent == "SOCIALIZE" and ceo_spoke: delta = 0 
                elif intent == "PANIC": delta = random.randint(-5, 0) # Panic ruins progress
                elif intent == "MITIGATE": delta = random.randint(0, 5) # Mitigating doesn't progress the sprint much
                elif intent == "DEEP_WORK": delta = random.randint(15, 25) 
                else: delta = random.randint(5, 12) 

            except Exception as llm_e:
                msg = "*Network latency. Holding position.*"
                stress = min_stress
                intent = "MITIGATE"
                delta = 0

            target_chan = "general"
            if org in ["ENG", "R&D"] and ("code" in msg.lower() or "kernel" in msg.lower() or "port" in msg.lower() or "audit" in msg.lower() or intent in ["MITIGATE", "PANIC"]): 
                target_chan = "dev-den"

            updated_task, new_trust = await self.vix_sys.update_task_and_trust.remote(name, delta, stress, ceo_spoke)
            
            color = "\033[92m" if stress <= 3 else "\033[93m" if stress <= 7 else "\033[91m"
            chan_color = "\033[94m" if target_chan == "dev-den" else "\033[97m"
            trust_color = "\033[92m" if new_trust >= 7.0 else "\033[93m" if new_trust >= 4.0 else "\033[91m"
            mole_icon = "🕵️ " if is_mole else ""
            
            await self.vix_sys.add_message.remote(time_str, name, target_chan, msg, severity=0)
            
            print(f"{color}🔥 [{name.upper()} | INTENT: {intent}] @ {time_str} | STRESS: {stress}/10 | {trust_color}TRUST: {new_trust}\033[0m {mole_icon}")
            print(f"   💼 TASK: {updated_task['name']} [{get_pbar(updated_task['prog'])}] {updated_task['prog']}% (+{delta}%)")
            print(f"   {chan_color}#{target_chan}\033[0m: {msg}\n")
            
        except Exception as e:
            print(f"\033[90m🔥 [{name.upper()}] @ {time_str} | STRESS: 5/10 | ERROR\033[0m")
            print(f"\033[91m   Traceback: {traceback.format_exc().strip().splitlines()[-1]}\033[0m\n")
            await self.vix_sys.update_task_and_trust.remote(name, 10, 5, False)
            
        self.tick_count += 1