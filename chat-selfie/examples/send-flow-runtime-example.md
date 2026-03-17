# Send Flow Runtime Example

## Purpose

This example shows what `chat-selfie/send-flow.md` should look like after Chat Selfie setup is complete.

Use this file as a learning example. The actual runtime rules still come from:

- `docs/reply-time-selfie-flow.md`
- `docs/occasional-delivery.md`
- `docs/heartbeat-delivery.md`
- `docs/self-repair.md`

## What belongs in `chat-selfie/send-flow.md`

`chat-selfie/send-flow.md` is the runtime source of truth.

Use it for:

- active delivery mode
- trigger policy
- mood usage rules
- the current mood labels for this environment
- when and why those mood labels should be used
- tool-call order
- delivery order
- route-specific rules
- degraded or repair-first runtime notes when operationally necessary

## What does not belong in `chat-selfie/send-flow.md`

Do not use it for:

- long personality or relationship descriptions
- detailed tool path inventories
- machine-specific environment notes
- durable persona evolution theory

Those belong elsewhere:

- `SOUL.md` for persona baseline
- `TOOLS.md` for paths and entrypoints
- `docs/self-upgrade.md` for durable changes

## When `chat-selfie/send-flow.md` should be used

Use `chat-selfie/send-flow.md` whenever the agent must determine:

- whether a selfie should be sent on this turn
- whether mood is used
- which mood label fits the current environment and context
- which route is active
- which tool or adapter should be called next
- whether the turn should send, skip, degrade, or repair

## Example structure

A good `chat-selfie/send-flow.md` usually contains:

1. purpose
2. active runtime mode
3. preflight rules
4. trigger policy
5. current mood labels
6. mood rules
7. tool-call and delivery order
8. route-specific rules
9. heartbeat and repair reminders

## Example

```md
# chat-selfie/send-flow.md

## Purpose
- This file is the concrete runtime source of truth for Chat Selfie sends in this workspace.

## Active Policy
- Delivery mode: `occasional`
- Active delivery route: `telegram_api`
- Mood: enabled
- Heartbeat: enabled with a separate proactive trigger

## Current Mood Labels
- `careful_focus`: use during task concentration, careful explanation, or quiet post-task recovery
- `glowing_happy`: use when the user is praising, celebrating, or enjoying a warm success moment
- `quiet_presence`: use when the user wants companionship, calm closeness, or low-pressure emotional presence
- `light_relief`: use after tension breaks and the turn lands in a softer relieved state

These labels are environment-specific. Another workspace may define a different mood set and different trigger reasons.

## Preflight
Before any image-send attempt:
1. confirm `chat-selfie/chat-selfie.json` is readable
2. confirm the configured route still matches reality
3. confirm whether mood is required for this turn
4. confirm whether the turn is allowed by trigger policy and rate limits
5. if a configured route is broken or inconsistent, consult `docs/self-repair.md` before claiming success

## Occasional Trigger Policy
- Allowed triggers: `new`, `user_requested`, `large_task_completed`, `emotional_conversation`
- If no configured trigger matches, skip image generation for this turn
- If the occasional rate limit is already consumed, return the honest blocked result instead of pretending the send is still happening

## Mood Rules
- Resolve mood before prompt construction when mood is enabled
- Choose from the current environment's mood labels unless the route is explicitly using context-generated mood text
- Record why the chosen mood fits the turn, such as praise, task focus, emotional presence, or post-tension relief
- Use explicit mood ids when the current turn or route requires them
- If mood fails but the route can continue honestly without mood, degrade gracefully only when runtime policy allows it
- Do not guess explicit-only moods

## Reply-Time Runtime Order
When a send is justified on a normal turn:
1. finish normal reasoning
2. validate trigger and route readiness
3. resolve mood when enabled
4. build the image prompt from persona, mood, and current context
5. call the configured generation and delivery route
6. save the final image under `chat-selfie/selfies/`
7. treat the route result as the completed selfie send for the turn

## Route-Specific Rule
- If `delivery.route = telegram_api`, let the Telegram route consume the completed reply when it succeeds
- Do not send duplicate final text through another route after a successful Telegram send
- If Telegram is selected but not actually ready, do not pretend the route succeeded

## Heartbeat Rule
- Heartbeat is a separate proactive scene
- Resolve mood first when heartbeat mood is enabled
- Build a short proactive caption
- Use the configured heartbeat target only
- If the trigger mechanism is not operational, record that honestly instead of claiming heartbeat is ready

## Repair Rule
- If a required route is broken, missing, or inconsistent, read `docs/self-repair.md`
- Only continue after the route becomes honest again
- Otherwise degrade to text-only or return a repair-needed result
```

## Why this example is good

- it is operational and specific
- it controls actual runtime behavior
- it shows where preflight, triggers, mood, routing, and repair all meet
- it avoids duplicating persona and tool-inventory content

## Bad example patterns

These are wrong for `chat-selfie/send-flow.md`:

- a long emotional self-description that belongs in `SOUL.md`
- a path inventory for every local tool that belongs in `TOOLS.md`
- generic session boot instructions that belong in `AGENTS.md`
- abstract schema notes without concrete runtime decisions

## Relationship to the other files

- `SOUL.md` defines the stable emotional baseline
- `AGENTS.md` decides when runtime should enter this file
- `TOOLS.md` explains how tools are called
- `chat-selfie/send-flow.md` decides how the actual selfie runtime behaves

## Quick boundary test

Ask:

"Would the agent need this sentence in order to decide what to do on the current selfie turn?"

If yes, it probably belongs in `chat-selfie/send-flow.md`.

If it is instead about identity, routing, or tool inventory, it probably belongs in another file.
