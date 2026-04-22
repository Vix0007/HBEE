# Changelog

All notable changes to the HBEE project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v34.0.0] - 2026-04-22
### Summary
Refactored the engine to support infinite runtimes ("Groundhog Day" loop), implemented nightly memory compaction to bound LLM context windows, and formalized a mathematically decaying "Suspicion Matrix" to track agent-to-agent paranoia dynamically.

### Added
- **Continuous Simulation Loop**: Removed the static 22-tick limit, enabling infinite runtimes with a continuous Day/Time cycle.
- **Context Compaction**: Clears raw channel history each night while carrying over persistent ledgers and daily summaries to maintain unbroken causality.
- **Suspicion Matrix & Pre-cuGraph Telemetry**: Introduced a 2D directed adjacency matrix tracking quantitative suspicion levels between agents. Added a secondary CSV (`vixero_edges.csv`) to log interaction weights for future GPU graph processing.

### Changed
- **State Hysteresis & Dynamic Isolation**: Suspicion scores now decay (-0.5 per tick) to stabilize relationships. Crossing an 8.0 threshold dynamically alters the target agent's causal constraints to forbid collaboration.
- **Telemetry Processing**: Consolidated I/O operations into the asynchronous `log_telemetry()` method to minimize Ray event loop blocking overhead.

---

## [v33.0.0] - 2026-04-22
### Summary
Transitioned to the `CitizenAgent` base class for macro-economy support. Resolved C++ backend schema validation crashes and implemented a robust XML parsing fallback system.

### Added
- **Interactive Command Queue**: Thread-safe terminal listener for live injection of `/fire`, `/env`, `/news`, and `/event` directives.
- **Ray Actor State Management**: `VixeroSystem` class handles global office state, channel history, and trust ledgers asynchronously.
- **HR Safety Directive**: Enforced prompt constraints for professional rejection of explicit or abusive inputs.

### Changed
- **XML Output Formatting & "Fuzzy Salvage" Parsing**: Replaced regex boundaries with XML tags. Implemented a dynamic tag-stripping parser to prevent complete message loss during LLM context shock or truncation.
- **Delta Logic**: Mapped task progression explicitly to LLM intent states (e.g., `DEEP_WORK` yields +15-25%, `PANIC` yields negative or zero progress).

### Fixed
- **C++ Backend Initialization Crash**: Resolved gRPC `RST_STREAM` and `KeyError` exceptions by restoring mandatory demographic attributes and utilizing strict dictionary schemas (`profile`, `base`, `status`).

---

## [v32.0.0] - 2026-04-20
### Summary
Hardened the engine against concurrency bottlenecks and LLM response timeouts under multi-agent loads.

### Added
- **Auto-logger**: Integrated continuous file logging (Tee stdout) with automated ANSI stripping for historical readability.
- **Concurrency Throttle**: Implemented async request jitter to prevent request bursts from overwhelming the local inference server.
- **RAW BRAIN DUMP Debugger**: Enabled verbose raw output logging upon structured extraction failure to aid prompt debugging.

---

## [v31.0.0] - 2026-04-20
### Summary
Introduced interactive runtime control and formalized the terminal UI visualization.

### Added
- **Terminal UI Layer**: Added ANSI color-coded stress states, dynamic progress bars, and channel-specific routing formats (`#general`, `#dev-den`).
- **System Event Bus**: Launched a detached Ray actor serving as the centralized message and state coordinator.
- **Dynamic Channel Routing**: Enabled support for prefixed channel targeting during runtime commands.

---

## [v30.0.0] - 2026-04-19
### Summary
Expanded from a single-agent architecture to a synchronized multi-agent environment with crisis scripting.

### Added
- **Multi-Agent Orchestration**: Implemented roster rotation, memory initialization, and physical AOI anchoring using compiled Protobuf maps.
- **Crisis Scripting Pipeline**: Built the framework for injecting high-severity events (e.g., "Zero-Day Attack") and triggering global intent overrides.
- **Task Progress Mechanics**: Implemented percentage-based tracking for individual agent deliverables.

---

## [v0.1.0] - 2026-04-19
### Summary
Initial project initialization, map compilation, and local LLM connectivity.

### Added
- **Local Inference Wiring**: Established bidirectional communication between AgentSociety, Ray, and a local vLLM API server.
- **Map Compilation**: Automated OpenStreetMap data ingestion and `.pb` map compilation.
- **Simulation Core**: Bootstrapped the foundational tick loop scheduling and GPU KV-cache warmup handling.