# Missing Requirements

Open Questions
- What platforms should the system support for final deployment (cloud, self-hosted, desktop)?
- Expected user interface: CLI-only, Web UI, or both?
- Authentication and multi-user requirements?
- Budget, rate-limits and preferred provider list for production runs?
- Persistence needs: retention policy, snapshots, artifact storage (git, object store)?
- CI/CD and repository integration expectations (GitHub/GitLab)?
- Licensing constraints for model usage (commercial vs research)?
- Testing expectations (unit, integration, E2E) and tooling choices.

Assumptions Required (record in assumptions.md)
- Default to self-hostable stack with cloud deployment option.
- Start with single-user mode for MVP.
