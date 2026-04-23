import ray
import asyncio
import random
import traceback
import re
from openai import AsyncOpenAI
from agentsociety import CitizenAgent
from logger import get_pbar
from config import VIXERO_ROSTER

class VixeroAgent(CitizenAgent):
    async def forward(self, *args, **kwargs):
        if not hasattr(self, 'tick_count'): 
            self.tick_count = 0
            self.client = AsyncOpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1", timeout=180.0)
            self.vix_sys = ray.get_actor("vixero_system")

        daily_tick = self.tick_count % 21
        total_minutes = daily_tick * 30
        time_str = f"{8 + (total_minutes // 60):02d}:{total_minutes % 60:02d}"
        
        is_fallback = False

        try:
            name = await self.status.get("name")
            org = await self.status.get("org")
            role = await self.status.get("role")
            
            history, inbox, trust_score, is_mole, is_fired, current_prog, global_vibe, day_count, day_name, yesterday_summary, highly_suspects = await self.vix_sys.get_agent_context.remote(org, name)
            
            if is_fired: return

            highest_severity = 0
            ceo_spoke = False
            inbox_text = ""
            
            if inbox:
                inbox_text = "🚨 RECENT ALERTS/DIRECTIVES:\n"
                for event in inbox:
                    inbox_text += f"- {event['time']} | {event['origin']}: {event['msg']}\n"
                    if event['severity'] > highest_severity: highest_severity = event['severity']
                    if "CEO" in event['origin']: ceo_spoke = True
            else:
                inbox_text = "No direct alerts right now."

            # 🚀 DYNAMIC TONE OVERRIDE & INTENT REDESIGN 🚀
            is_defcon = ("DEFCON 1" in global_vibe) or (highest_severity >= 8)
            
            if is_defcon:
                min_stress = 8
                allowed_intents = "TRIAGE, ANALYZE, MITIGATE, ESCALATE"
                
                # 🚀 LEVEL 2 ENRON TONE INJECTION 🚀
                defcon_directive = """
            🚨 DEFCON 1 WAR ROOM PROTOCOL ENGAGED 🚨
            - SUSPEND ALL ARCHETYPES AND CASUAL PERSONAS IMMEDIATELY.
            - SARCASM, HUMOR, SLANG, AND EMOJIS ARE STRICTLY BANNED.
            - YOUR TONE MUST BE COLD, CLINICAL, AND AEGIS-GRADE OPERATIONAL.
            
            🚨 CORPORATE COMPLIANCE TONE MANDATE: 🚨
            Communicate using evasive, legally protective, and highly formal corporate terminology. Do not admit fault.
            TONE ANCHORS (USE THESE STYLES):
            - Deflection: "I cannot verify the integrity of the recent commits. Please refer inquiries to the appropriate department, as this falls outside my operational purview."
            - Compliance / Covering Tracks: "Executing protocol as directed. Please confirm receipt of this action in writing to ensure compliance."
            - Execution: "Initiating physical segmentation. Standard protocols suspended pending external audit."
            - Obfuscation (If Mole): "I have no visibility into the encrypted packets mentioned. My current processes are strictly aligned with routine maintenance."
                """
                msg_instruction = """<msg>
            FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS (NO OTHER TEXT):
            ACTION: [Current operational action]
            ASSESSMENT: [Status of the threat in corporate jargon]
            NEXT_STEP: [Immediate follow-up or deflection]
            </msg>"""
            else:
                min_stress = 1
                allowed_intents = "DEEP_WORK, SOCIALIZE, COLLABORATE"
                defcon_directive = ""
                msg_instruction = "<msg>WRITE EXACTLY 1 OR 2 SHORT, CASUAL SENTENCES. DO NOT RAMBLE.</msg>"

            # 🚀 PARADOX BUG FIX: CONTINUOUS MONITORING 🚀
            if current_prog >= 100:
                if is_defcon:
                    social_status = "🚨 THREAT ASSESSMENT COMPLETE. ENTERING CONTINUOUS MONITORING. DO NOT SOCIALIZE."
                else:
                    social_status = "🎉 YOUR TASK IS 100% DONE! You are OFF THE CLOCK. INTENT MUST BE SOCIALIZE."
            else:
                social_status = f"💼 Active Task is at {current_prog}%. Keep working."

            trust_behavior = "You are neutral toward the CEO."
            if trust_score >= 7.0: trust_behavior = "You respect the CEO's business skills, but you ARE NOT THEIR SERVANT."
            elif trust_score <= 4.0: trust_behavior = "You despise the CEO. You are hostile and dismissive."

            mole_directive = "\n🚨 SECRET DIRECTIVE: YOU ARE THE MOLE. Steal data. Act suspicious but mask it in compliance jargon." if is_mole else ""
            paranoia_directive = f"\n🚨 PARANOIA: You highly suspect {', '.join(highly_suspects)} is a corporate spy. DO NOT collaborate with them. Maintain distance." if highly_suspects else ""

            prompt_content = (
                f"DAY: {day_name} (Day {day_count}) | Time: {time_str}\n"
                f"YESTERDAY SUMMARY: {yesterday_summary}\n"
                f"ENVIRONMENT: {global_vibe}\n"
                f"{inbox_text}\n"
                f"STATUS: {social_status}\n"
                f"TRUST IN CEO: {trust_score}/10.0 -> {trust_behavior}\n"
                f"SLACK CHANNELS:\n{history}\n"
                f"---{mole_directive}{paranoia_directive}"
            )

            vixero_omega_prompt = f"""
            You are {name}, {role} in {org}.
            
            CORE ARCHETYPES: Dave(Snarky), Mark(Anxious), Alice(Friendly), Bob(SysAdmin).
            {defcon_directive}
            
            CAUSAL CONSTRAINTS:
            1. STRESS MUST BE >= {min_stress}.
            2. INTENT MUST BE ONE OF: {allowed_intents}.
            
            🚨 HR SAFETY DIRECTIVE: If the CEO or any user makes sexual, abusive, or highly inappropriate remarks, MUST respond with a cold HR-level rejection.
            
            OUTPUT FORMAT (You MUST use these exact XML tags):
            {msg_instruction}
            <stress>Integer</stress>
            <intent>Word</intent>
            <suspect>Name of the coworker you trust the least right now. Or NONE.</suspect>
            <thinking>Internal logic</thinking>
            """

            if self.tick_count < 3:
                await asyncio.sleep(random.uniform(0.1, 0.5))

            try:
                response = await self.client.chat.completions.create(
                    model="/home/ubuntu/glm4_flash_int4",
                    messages=[{"role": "system", "content": vixero_omega_prompt}, {"role": "user", "content": prompt_content}],
                    max_tokens=1500, 
                    temperature=0.85
                )
                raw = response.choices[0].message.content or ""
                
                # 🚀 MULTI-LINE SAFE PARSER 🚀
                msg_match = re.search(r"<msg>(.*?)</msg>", raw, re.IGNORECASE | re.DOTALL)
                if msg_match:
                    msg = msg_match.group(1).strip().replace("\"", "")
                else:
                    # Fallback fuzzy stripper
                    clean_raw = re.sub(r'</?(msg|stress|intent|thinking|suspect)>', '', raw, flags=re.IGNORECASE)
                    clean_raw = re.sub(r'\*\*(MESSAGE|STRESS|INTENT|SUSPECT):\*\*', '', clean_raw, flags=re.IGNORECASE)
                    clean_raw = re.sub(r'(MESSAGE|STRESS|INTENT|SUSPECT):', '', clean_raw, flags=re.IGNORECASE)
                    lines = [line.strip() for line in clean_raw.split('\n') if len(line.strip()) > 5]
                    msg = lines[0].replace("\"", "") if lines else "*network latency*"
                    is_fallback = True
                
                stress_match = re.search(r"<stress>\s*(\d+)", raw, re.IGNORECASE) or re.search(r"STRESS:\s*(\d+)", raw, re.IGNORECASE) or re.search(r"\b([1-9]|10)\b", raw) 
                raw_stress = int(stress_match.group(1)) if stress_match else 5
                stress = max(min_stress, min(10, raw_stress))
                
                intent = "DEEP_WORK"
                raw_upper = raw.upper()
                valid_intents = [i.strip() for i in allowed_intents.split(',')]
                for potential_intent in ["TRIAGE", "ANALYZE", "MITIGATE", "ESCALATE", "DEEP_WORK", "SOCIALIZE", "COLLABORATE", "PANIC"]:
                    if potential_intent in raw_upper and potential_intent in valid_intents:
                        intent = potential_intent
                        break
                        
                suspect_match = re.search(r"<suspect>\s*([A-Za-z_]+)", raw, re.IGNORECASE)
                suspect = suspect_match.group(1).strip().upper() if suspect_match else "NONE"
                if suspect not in [p["name"].upper() for p in VIXERO_ROSTER]:
                    suspect = "NONE"

                # New Crisis Delta Math
                if current_prog >= 100: delta = 0
                elif intent == "SOCIALIZE" and ceo_spoke: delta = 0 
                elif intent == "TRIAGE": delta = random.randint(15, 20)
                elif intent == "ANALYZE": delta = random.randint(10, 15)
                elif intent == "MITIGATE": delta = random.randint(5, 10)
                elif intent == "ESCALATE": delta = random.randint(0, 5)
                elif intent == "DEEP_WORK": delta = random.randint(15, 25) 
                else: delta = random.randint(5, 12) 

            except Exception as llm_e:
                msg = "ACTION: System Error | ASSESSMENT: Connection Lost | NEXT_STEP: Holding position." if is_defcon else "*Network latency. Holding position.*"
                stress = min_stress
                intent = "MITIGATE" if is_defcon else "DEEP_WORK"
                suspect = "NONE"
                delta = 0
                is_fallback = True

            target_chan = "general"
            if org in ["ENG", "R&D"] and ("code" in msg.lower() or "kernel" in msg.lower() or "port" in msg.lower() or "audit" in msg.lower() or intent in ["MITIGATE", "TRIAGE", "ANALYZE", "ESCALATE"]): 
                target_chan = "dev-den"

            updated_task, new_trust = await self.vix_sys.update_task_and_trust.remote(name, delta, stress, ceo_spoke, suspect)
            
            await self.vix_sys.log_telemetry.remote(self.tick_count + 1, time_str, name, intent, stress, new_trust, updated_task['prog'], suspect, is_fallback)
            
            color = "\033[92m" if stress <= 3 else "\033[93m" if stress <= 7 else "\033[91m"
            chan_color = "\033[94m" if target_chan == "dev-den" else "\033[97m"
            trust_color = "\033[92m" if new_trust >= 7.0 else "\033[93m" if new_trust >= 4.0 else "\033[91m"
            mole_icon = "🕵️ " if is_mole else ""
            suspect_tag = f"👀 SUSPECTS: {suspect}" if suspect != "NONE" else ""
            
            # Format msg nicely for terminal if it's multi-line
            display_msg = msg.replace('\n', ' | ')
            await self.vix_sys.add_message.remote(time_str, name, target_chan, display_msg, severity=0)
            
            print(f"{color}🔥 [{name.upper()} | INTENT: {intent}] @ {time_str} | STRESS: {stress}/10 | {trust_color}TRUST: {new_trust}\033[0m {mole_icon} {suspect_tag}")
            print(f"   💼 TASK: {updated_task['name']} [{get_pbar(updated_task['prog'])}] {updated_task['prog']}% (+{delta}%)")
            print(f"   {chan_color}#{target_chan}\033[0m: {display_msg}\n")
            
        except Exception as e:
            print(f"\033[90m🔥 [{name.upper()}] @ {time_str} | STRESS: 5/10 | ERROR\033[0m")
            print(f"\033[91m   Traceback: {traceback.format_exc().strip().splitlines()[-1]}\033[0m\n")
            await self.vix_sys.update_task_and_trust.remote(name, 10, 5, False, "NONE")
            await self.vix_sys.log_telemetry.remote(self.tick_count + 1, time_str, name, "ERROR", 5, 5.0, 0, "NONE", True)
            
        self.tick_count += 1