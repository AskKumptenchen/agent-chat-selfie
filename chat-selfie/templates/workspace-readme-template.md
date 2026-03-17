# Chat Selfie Workspace

This directory was created for one target agent's Chat Selfie setup.

## Purpose

Store the local state needed for Chat Selfie initialization and later maintenance.

`send-flow.md` in this directory should remain the runtime source of truth for image-delivery order, trigger policy, mood usage, and route behavior.

## Important local files

- `chat-selfie.json`: main runtime config
- `startup.answers.json`: normalized startup answers
- `startup.record.json`: readiness and repair state
- `integration.md`: notes about persona and tool integration
- `status.md`: current setup state
- `send-flow.md`: concrete runtime send order, trigger policy, mood catalog, and route rules

## Ownership

- Files in this directory are local workspace state.
- Files under `adapters/` are user-owned custom adapters.
- Repository-owned tool contracts live in the installed Chat Selfie package and may be updated separately.
- External memory files such as `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and `SOUL.md` should point back to `send-flow.md` when runtime image delivery depends on Chat Selfie.
- Durable persona or mood evolution should consult `docs/self-upgrade.md` before rewriting long-term mood rules or emotional baseline files.
