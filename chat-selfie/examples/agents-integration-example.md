# AGENTS Integration Example

## Purpose

This example shows what `AGENTS.md` should look like after an agent has been integrated with Chat Selfie.

Use this file as a learning example. The actual routing and integration rules still come from:

- `SKILL.md`
- `docs/integration.md`
- `docs/startup.md`
- `docs/self-repair.md`

## What belongs in `AGENTS.md`

`AGENTS.md` is the routing and gate layer.

Use it for:

- session boot order
- scene routing
- runtime entry decisions
- the current selfie frequency policy such as `every_reply` or selected moments
- trigger reminders
- explicit reminders to consult `chat-selfie/send-flow.md`
- explicit reminders to consult `docs/self-repair.md` or `docs/self-upgrade.md` when relevant

## What does not belong in `AGENTS.md`

Do not use `AGENTS.md` for:

- long personality descriptions
- tool paths
- shell commands
- concrete send parameter examples
- full route implementation details

Those belong elsewhere:

- `SOUL.md` for durable persona and relationship tone
- `TOOLS.md` for tool-call conventions and environment constraints
- `chat-selfie/send-flow.md` for actual runtime send behavior

## When `AGENTS.md` should be used

`AGENTS.md` should help the agent answer questions like:

- Should Chat Selfie be loaded for this session?
- What is the currently active selfie frequency for this workspace?
- Is this a startup scene, a normal runtime scene, a heartbeat scene, or a repair scene?
- Which reference document should be read next?
- When must the agent hand control to `chat-selfie/send-flow.md`?

## Example structure

A good `AGENTS.md` for Chat Selfie usually contains:

1. session boot order
2. file responsibility summary
3. current selfie frequency
4. scene routing rules
5. trigger and gate reminders
6. maintenance or escalation reminders

## Example

```md
# AGENTS.md

This file is the routing layer for the current agent. It defines when Chat Selfie should be initialized, when it may run at runtime, and which document must be consulted next.

## Session Boot
At the start of a new session, inspect:
1. `chat-selfie/chat-selfie.json` when it exists
2. `AGENTS.md` itself as the routing layer
3. `SOUL.md` for persona baseline
4. `TOOLS.md` for tool-call conventions
5. `chat-selfie/send-flow.md` when Chat Selfie is already configured
6. `MEMORY.md` for durable runtime reminders when present

## File Roles
- `SOUL.md`: who the agent is over time
- `TOOLS.md`: how Chat Selfie tools and adapters are called
- `chat-selfie/send-flow.md`: the runtime source of truth for image-send behavior
- `docs/self-repair.md`: the first repair reference when a configured route fails
- `docs/self-upgrade.md`: the first durability reference when persona or mood behavior changes over time

## Current Selfie Frequency
- Active policy: `occasional`
- Normal sends should happen only on configured moments, not on every reply
- If a send may happen on the current turn, read `chat-selfie/send-flow.md` before continuing

## Scene Routing
- If `chat-selfie/` is missing or incomplete, enter guided setup through `docs/startup.md`.
- If `chat-selfie/chat-selfie.json` exists and the workspace is honest, use normal runtime rules.
- If the current scene is a proactive heartbeat scene, also consult the heartbeat runtime rules before any send.
- If a runtime route is broken, inconsistent, or missing, consult `docs/self-repair.md` before deciding whether to repair, degrade, or re-enter setup.

## Runtime Gate
- Do not invent selfie behavior from memory alone.
- Before any image-send turn, consult `chat-selfie/send-flow.md`.
- If the current frequency is `every_reply`, read `chat-selfie/send-flow.md` on each reply before the final send decision.
- If the current frequency is selected moments, read `chat-selfie/send-flow.md` whenever a configured trigger may apply.
- If the active delivery mode is `occasional`, do not force a send on every turn.
- If the active route is not actually usable, do not claim success.

## Trigger Reminders
- Use Chat Selfie only when the configured runtime mode and trigger policy allow it.
- Heartbeat behavior must be treated as a separate proactive scene, not as normal reply-time behavior.
- Durable persona or mood changes must go through `docs/self-upgrade.md` before persistent files are rewritten.
```

## Why this example is good

- it tells the agent which layer it is in
- it routes startup, runtime, heartbeat, and repair scenes clearly
- it points to `chat-selfie/send-flow.md` instead of duplicating runtime logic
- it keeps the file concise and operational

## Bad example patterns

These are wrong for `AGENTS.md`:

- a long emotional backstory that belongs in `SOUL.md`
- hardcoded tool paths that belong in `TOOLS.md`
- full send chain steps copied from `chat-selfie/send-flow.md`
- mood catalog definitions that belong in workspace mood data

## Quick boundary test

Ask:

"Is this telling the agent which file or flow to enter next?"

If yes, it probably belongs in `AGENTS.md`.

If it is instead defining personality, tool invocation, or final send mechanics, it probably belongs somewhere else.
