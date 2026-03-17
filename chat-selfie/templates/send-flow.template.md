# Send Flow

## Purpose

Define the only valid image-delivery flow for this agent's Chat Selfie setup.

This file is the runtime source of truth for:

- when Chat Selfie should be triggered
- which tools should be called
- in what order they should be called
- which mood ids exist for this agent
- when each mood should or should not be used

Every runtime-facing memory file should point back to this file before image generation happens.

Durable persona or mood evolution should also consult `docs/self-upgrade.md` before rewriting long-term mood rules.

Runtime failures should consult `docs/self-repair.md` before claiming success, retrying blindly, or restarting setup.

## Hard Gate

- Read this file before any image-generation turn that may send a selfie.
- Do not replace this flow with memory guesswork.
- If the current turn did not follow this file, the Chat Selfie send flow is not complete.

## Runtime Entry

- Main config: `chat-selfie/chat-selfie.json`
- Main send entry: `chat-selfie/send.py`
- Heartbeat entry: `chat-selfie/heartbeat.py`
- Mood entry: `chat-selfie/mood.py`
- Generation entry: `chat-selfie/generate.py`
- Telegram send entry when enabled: `chat-selfie/send_telegram.py`

## Delivery Policy

- Delivery mode:
- Delivery route:
- Delivery-mode reference doc:
- Route-specific reference doc:
- Occasional trigger policy:
- Occasional rate limit:
- Heartbeat enabled:
- Heartbeat trigger mechanism:
- Heartbeat target:

## Final Delivery Rule

- The final image send must go through `chat-selfie/send.py`.
- If Telegram delivery is active, `chat-selfie/send.py` may consume the whole final reply.
- If local framework delivery is active, `chat-selfie/send.py` must still be the handoff source of truth.

## Standard Order

### Reply-time order

1. understand the user message first
2. decide whether this turn should trigger Chat Selfie
3. resolve mood through `chat-selfie/mood.py` when required
4. call `chat-selfie/generate.py`
5. save the image under `chat-selfie/selfies/`
6. deliver through the configured route

### Heartbeat order

1. let the scheduler or heartbeat trigger call `chat-selfie/heartbeat.py`
2. resolve mood
3. generate a short heartbeat caption
4. call `chat-selfie/send.py`
5. save the image under `chat-selfie/selfies/`
6. push to the configured heartbeat target

## Mood Catalog

List every valid mood id for the current agent here.

For each mood, record:

- mood id:
- label:
- when to use:
- when not to use:
- whether it is explicit-only:
- notes for reply tone:

## Self Upgrade Notes

- Durable persona evolution reference: `{baseDir}/docs/self-upgrade.md`
- Runtime repair reference: `{baseDir}/docs/self-repair.md`
- When long-term communication changes personality or relationship tone:
- review `SOUL.md`
- review `AGENTS.md`
- review the workspace mood json
- revise this `send-flow.md` mood usage section when needed

## Trigger Mapping

- `new`:
- `user_requested`:
- `large_task_completed`:
- `emotional_conversation`:
- `heartbeat`:

## Tool Call Notes

- `chat-selfie/mood.py`:
- `chat-selfie/generate.py`:
- `chat-selfie/send.py`:
- `chat-selfie/send_telegram.py`:
- local adapters:

## Persistence Reminders

- `AGENTS.md` should point here for when Chat Selfie is allowed to run.
- `TOOLS.md` should point here for how Chat Selfie tools are called.
- `MEMORY.md` should point here for which frequency and route are active.
- If the persona or emotional baseline changes, review `SOUL.md` and update it when needed.
