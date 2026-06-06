# Architecture Review

Key Decisions
- Use a provider abstraction layer to avoid vendor lock-in.
- FastAPI backend and Next.js frontend (per workspace specs) as the initial stack.
- SQLite for initial persistence; design pluggable storage adapter.

Tradeoffs
- Provider abstraction increases initial complexity but enables future-proofing.
- SQLite is simple and reliable for single-node MVP but will need migration for scale.
- FastAPI + Next.js split increases deployment complexity versus single-stack monolith.

Potential Bottlenecks
- Model latency and rate limits for large-scale parallel tasks.
- Token cost for large planning/segmentation work.
- Single-node database (SQLite) IO under heavy concurrency.

Scalability Concerns
- Need to shard task queues and add worker autoscaling for parallel builds.
- Centralized embedding store and vector DB needed for large projects.
- Provider rate-limit handling and intelligent routing required.
