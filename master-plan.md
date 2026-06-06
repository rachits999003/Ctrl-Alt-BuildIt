# Ctrl Alt BuildIt! — Master Plan

Product Vision
- An autonomous software builder that converts high-level project requests into a working MVP and iteratively improves it.

System Architecture (high level)
- Frontend: Next.js + TypeScript + Tailwind (+ shadcn components)
- Backend: FastAPI (task orchestration, provider manager, verification gates)
- Storage: SQLite for initial metadata, pluggable to Postgres for scale
- Providers: Model Provider Manager implementing a universal interface (generate, chat, stream, embeddings, tool_calls, health_check, model_info)
- Orchestration: Autonomous execution loop (plan → segment → implement → test → verify → fix → summarize → replan)

Major Components
- Master Orchestrator (task scheduler, state manager)
- Prompt Segmenter (break features into implementation prompts)
- Planner / Roadmap Manager
- Provider Manager (model abstraction + connector registry)
- Implementation Engine (code generation + apply patches)
- Test Engine (unit/integration test harness)
- Verification & Reporter (build-report generator)
- Persistence & Checkpointing (project-state.json, snapshots)

Risks
- Model capability variance and incompatibilities across providers (streaming, tool-calls, vision)
- Rate limits, latency, and cost of remote models
- Security and secrets management for arbitrary endpoints
- Automatic code application risks (breaking builds) — requires safe rollback/checkpointing
- Ambiguity in user requirements leading to wasted work

Build Strategy
- Phase 1: Minimal MVP — provider-agnostic orchestration, prompt segmentation, simple planner, execution loop with a single local/remote provider, verification gates
- Phase 2: Add dynamic model routing, Ollama discovery, provider health checks, embeddings store
- Phase 3: Scale persistence, multi-provider failover, CI integration, UI polishing

MVP Definition
- User provides a project brief
- System plans a scoped MVP and decomposes into tasks
- System generates code for at least one working feature, runs build/tests, and reports success
- Provider abstraction implemented so models can be swapped via config

Next Steps
- Validate unanswered questions in [missing-requirements.md](missing-requirements.md)
- Start implementing Provider Manager interface and a simple orchestrator loop
