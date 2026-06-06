# Clarification Log

Open Questions to Ask the User
- Deployment target(s): self-hosted, cloud provider, or both? Ans: Both but prefer self hosted for now
- Intended audience and multi-user support requirements? Ans: Single user is fine for now
- Preferred providers and a list of allowed models for production runs? Ans: All free AI apis and ollama quen and deepseek code
- Data retention and artifact storage preferences? Ans: md files to act as a memory and used when needed
- Are there any security/compliance constraints (e.g., PII handling)? Ans: Follow the industry standards because this is mainly going to be used by me and also my friends from github.

Recorded Answers (2026-06-06)
- Deployment targets: Both cloud and self-hosted; prefer self-hosted for now.
- Audience / multi-user: Single-user for MVP.
- Preferred providers: All free AI APIs plus Ollama Qwen and DeepSeek Code models.
- Data retention: Markdown files used as memory and referenced when needed.
- Security / compliance: Follow industry standards; primarily for personal and trusted collaborators.

Next Steps
- Proceed to implement Provider Manager skeleton (universal interface, config-driven providers, Ollama discovery).
- Use markdown-based memory store for artifacts and assumptions.
- Continue with Provider Manager implementation unless new clarifications arise.
