<div align="center">

**Vickson Ferrel** · Founder, Vixero Technology Enterprise

[![arXiv](https://img.shields.io/badge/arXiv-2604.02149-b31b1b?style=flat&logo=arxiv)](https://arxiv.org/abs/2604.02149)
[![NVIDIA Inception](https://img.shields.io/badge/NVIDIA-Inception_Member-76b900?style=flat&logo=nvidia)](https://www.nvidia.com/en-us/startups/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Vix0007-FFD21E?style=flat&logo=huggingface)](https://huggingface.co/Vix0007)
[![GitHub](https://img.shields.io/badge/GitHub-Vix0007-181717?style=flat&logo=github)](https://github.com/Vix0007)
[![Website](https://img.shields.io/badge/Web-vixdev.cloud-0066CC?style=flat&logo=cloudflare)](https://vixdev.cloud)

*Vixero Technology Enterprise · Kuching, Sarawak, Malaysia*

</div>

# HBEE — Human Behavioral Entropy Engine

> *"Malware doesn't just compromise systems. It propagates through people."*

**HBEE** is a sociotechnical security simulation framework that models the human behavioral layer of enterprise network breaches. It simulates a realistic corporate environment — complete with office social dynamics, stress responses, and authentic human entropy — to study how malware propagates not just through networks, but through *organizations*.

HBEE is the research companion to [AEGIS](https://arxiv.org/abs/2604.02149), a thermodynamic network intrusion detection system. Where AEGIS detects the *network physics* of adversarial traffic, HBEE generates the *human context* that surrounds a real breach.

---

## The Problem

Modern cybersecurity sandboxes are fake. Sophisticated malware — particularly sandbox-aware and autonomous variants — detects the absence of genuine human activity and goes dormant. A sandbox with no gossip, no stress, no one clicking the wrong link at 2PM because they just got a passive-aggressive email from HR, is not a convincing enterprise environment.

Existing simulation frameworks model either:
- **Network behavior** (packet flows, lateral movement, C2 beaconing), or
- **Human behavior** (social dynamics, organizational psychology)

Nobody has modeled both simultaneously in the same environment. That gap is what HBEE fills.

---

## What HBEE Does

HBEE simulates a realistic corporate environment with **150 agents** across departments (R&D, Engineering, Operations), each with:

- **Persistent emotional states** — Dave is still angry at 2PM if he was angry at 9AM
- **Stress tracking** — deadlines, interpersonal conflict, and environmental stressors compound over time
- **Social graph** — trust scores, clique formation, communication patterns
- **Authentic behavioral entropy** — agents use mock internet, slack each other, form opinions

Adversarial events are injected — zero-day deployment, social engineering attacks, insider threats, network breaches — and HBEE measures how they propagate through the human layer before, during, and after detection.

---

## Why This Matters for Security

**The Human Entropy Horizon** — AEGIS V3 identifies a fundamental detection limit: flow-based thermodynamic detection cannot distinguish between a direct human connection and a perfectly mimicked human proxy. This means adversaries who operate at human speeds approach invisibility.

HBEE exists to study this horizon from the inside. By generating ground-truth behavioral data during a breach scenario, HBEE provides:

1. **Authentic entropy corpus** for training next-generation detectors (PELT — AEGIS V4)
2. **Behavioral signatures** of insider threats, compromised endpoints, and social engineering
3. **Blast radius modeling** — given a breach point, which agents are affected and how fast

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   HBEE Stack                    │
├─────────────────────────────────────────────────┤
│  AgentSociety 1.1.3 (Tsinghua FIB Lab)          │
│  150 agents | 20-min/tick clock                 │
├─────────────────────────────────────────────────┤
│  GLM-4.7 Flash int4 via vLLM                    │
│  Preserved Thinking + Interleaved Thinking      │
│  Emotional state continuity across ticks        │
├─────────────────────────────────────────────────┤
│  NVIDIA RAPIDS cuGraph                          │
│  Social graph analytics | Blast radius queries  │
├─────────────────────────────────────────────────┤
│  RTX 3090 24GB | Ubuntu 22.04 | CUDA 13.2       │
└─────────────────────────────────────────────────┘
```

**Why GLM-4.7?** GLM-4.7's Preserved Thinking and Interleaved Thinking modes maintain emotional and cognitive state continuity across multi-turn simulation ticks natively — without external state management hacks. If Dave is frustrated at tick 3, he is still frustrated at tick 7. This is the core requirement for authentic behavioral simulation and the primary reason GLM-4.7 was chosen over alternatives.

---

## Research Context

HBEE sits at the intersection of:
- **Multi-agent social simulation** (prior work: Smallville, AgentSociety)
- **Sociotechnical systems security** (largely uncrowded academic niche)
- **Adversarial corpus generation** for ML-based intrusion detection

The nearest prior work is Stanford's Smallville (Park et al., 2023) — 25 agents in a social environment. HBEE extends this to a **security-instrumented corporate simulation** with adversarial event injection, stress metrics, trust scoring, and ground-truth breach propagation logging.

**Target venues:** USENIX Security 2027, IEEE S&P

---

## Connection to AEGIS

```
AEGIS (V3)          HBEE                    PELT (V4)
Network physics  +  Human behavioral  →     Adaptive
thermodynamic       entropy corpus           detector
detection           generation               training
```

HBEE generates what AEGIS cannot see: the human layer. Together they close the detection gap that nation-state adversaries currently exploit.

- AEGIS paper: [arXiv:2604.02149](https://arxiv.org/abs/2604.02149)
- Dataset: [Vix0007/AEGIS-Adversarial-Corpus](https://huggingface.co/datasets/Vix0007/AEGIS-Adversarial-Corpus)

---

## Status

> **Phase 1 — Active** (April 2026)
> Stable simulation environment. Agents running. Trust scoring, stress tracking, and adversarial event injection operational.

---

## Author

**Vickson Ferrel** | Founder, Vixero Technology Enterprise
Universiti Malaysia Sarawak (UNIMAS) | arXiv Researcher | NVIDIA Inception Member

- arXiv: [2604.02149](https://arxiv.org/abs/2604.02149)
- HuggingFace: [Vix0007](https://huggingface.co/Vix0007)
- Web: [vixdev.cloud](https://vixdev.cloud)

---

*For Humanity, From Humanity. 🇲🇾*