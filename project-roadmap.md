# Project Roadmap

Stage 1: MVP
- Provider Manager (interface + one connector)
- Basic Orchestrator loop (plan → segment → implement → test → verify)
- Prompt Segmenter
- Minimal frontend or CLI to accept briefs
- Verification gates (build, tests)

Stage 2: Core Features
- Ollama discovery and connectors for OpenAI-compatible endpoints
- Dynamic model routing and per-task model selection
- Embeddings support and vector store integration
- Checkpointing, snapshots, and rollback

Stage 3: Enhancements
- Multi-user multi-project support
- CI/CD integration and repo sync
- Cost-aware routing and token accounting
- Advanced planners and heuristics

Stage 4: Polish
- UX improvements, dashboards, visual planners
- Security hardening and RBAC
- Internationalization

Stage 5: Optimization
- Autoscaling workers, performance profiling
- Caching, deduplication of model calls
- Advanced scheduling and prioritization
