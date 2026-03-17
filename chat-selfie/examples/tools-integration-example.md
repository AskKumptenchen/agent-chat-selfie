# TOOLS Integration Example

## Purpose

This example shows what `TOOLS.md` should look like after an agent has been integrated with Chat Selfie.

Use this file as a learning example. The actual tool and route responsibilities still come from:

- `docs/integration.md`
- `SKILL.md`
- `tools/README.md`
- route-specific docs under `docs/`

## What belongs in `TOOLS.md`

`TOOLS.md` is the tool-call and environment layer.

Use it for:

- important workspace paths
- script entrypoints
- adapter locations
- concrete mood, send-flow, send, and seed-related tool locations
- environment constraints
- when each tool should be called when that timing is operationally important
- argument-shape reminders when they are operationally important
- reminders about which runtime document controls actual send behavior

## What does not belong in `TOOLS.md`

Do not use `TOOLS.md` for:

- personality rules
- emotional baseline
- complete trigger policy explanations
- full delivery order
- the full per-turn send chain

Those belong elsewhere:

- `SOUL.md` for persona
- `AGENTS.md` for routing and gate decisions
- `chat-selfie/send-flow.md` for actual runtime send behavior

## When `TOOLS.md` should be used

`TOOLS.md` should help the agent answer questions like:

- Which script or adapter path should I call?
- Where is the seed helper or seed source for this environment?
- Which local runtime constraints matter here?
- Which environment limitation prevents an unsafe assumption?
- Where is the correct runtime source of truth if I need the actual send order?

## Example structure

A good `TOOLS.md` for Chat Selfie usually contains:

1. workspace paths
2. key Chat Selfie entrypoints
3. seed and helper locations
4. adapter or contract locations
5. environment constraints
6. a clear reminder that runtime behavior still belongs in `chat-selfie/send-flow.md`

## Example

```md
# TOOLS.md

Only store operational facts here: paths, entrypoints, adapter locations, and environment constraints.

## Main Paths
- Workspace root: `./`
- Chat Selfie workspace: `./chat-selfie`
- Runtime config: `./chat-selfie/chat-selfie.json`
- Runtime send rules: `./chat-selfie/send-flow.md`
- Local adapters: `./chat-selfie/adapters/`
- Portrait directory: `./chat-selfie/portrait/`
- Generated images: `./chat-selfie/selfies/`

## Chat Selfie Entrypoints
- Startup and integration entry: `SKILL.md`
- Mood entry: `chat-selfie/mood.py`
- Heartbeat entry: `chat-selfie/heartbeat.py`
- Send entry: `chat-selfie/send.py`
- Telegram send route when configured: `chat-selfie/send_telegram.py`

## Seed And Generation Helpers
- Seed source or helper: `chat-selfie/seed.py` or the environment-specific equivalent when one exists
- If a seed helper exists, use it during prompt or generation preparation when the current runtime route expects reproducible image state
- If this workspace has no standalone seed helper, record that truthfully instead of inventing one

## Repository Contracts
- Repository-owned contracts live under `tools/`
- Read repository contracts before assuming that a local adapter should be created or replaced

## Local Adapter Notes
- Workspace-owned adapters live under `chat-selfie/adapters/`
- Do not overwrite existing local adapters unless the user explicitly asked for that level of change
- If runtime policy allows a missing stub to be recreated, use the repair flow before inventing new behavior

## Environment Constraints
- Do not assume one fixed image backend exists
- Reuse an existing system capability when available
- Do not claim a route succeeded unless the configured route is actually ready
- Use `docs/self-repair.md` before attempting repair-like route fixes

## Runtime Reminder
- `TOOLS.md` explains how tools are called
- `TOOLS.md` may say when mood, seed, send, or heartbeat entries are called at a high level
- `chat-selfie/send-flow.md` explains when and in what order they are used
- Do not copy the full send chain into this file
```

## Why this example is good

- it gives operational facts without becoming a runtime policy file
- it defines where tools live and how they should be treated
- it makes the boundary with `chat-selfie/send-flow.md` explicit
- it helps prevent accidental overwriting of user-owned adapters

## Bad example patterns

These are wrong for `TOOLS.md`:

- "The agent should sound shy and warm." That belongs in `SOUL.md`.
- "Use occasional sends for emotional moments." That belongs in `chat-selfie/send-flow.md`.
- "On session boot, route to startup if the workspace is missing." That belongs in `AGENTS.md`.
- a full multi-step per-turn send procedure copied from runtime docs

## Quick boundary test

Ask:

"Is this telling me how to locate or call a tool, or is it telling me how runtime behavior should work?"

If it is about locating or calling tools, it probably belongs in `TOOLS.md`.

If it is about deciding runtime behavior, it probably belongs in `AGENTS.md` or `chat-selfie/send-flow.md`.
