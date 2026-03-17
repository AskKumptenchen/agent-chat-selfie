# Heartbeat Delivery

## Goal

Define how Chat Selfie should perform proactive heartbeat pushes when the user enables them.

Because timer and scheduler capabilities vary across agent environments, this repository does not provide one fixed scheduler implementation.

Instead, the skill should guide the agent to use:

1. a scheduled task when available
2. another heartbeat-capable runtime trigger only when a scheduled task is not the practical option

Scheduled tasks are the preferred route.

## Trigger rule

Heartbeat pushes should only run when heartbeat is enabled in the workspace config.

When heartbeat is enabled, the agent should retain:

- the preferred trigger mechanism
- the push interval
- the configured target location
- whether mood should be used during heartbeat pushes

## Runtime flow

When the scheduled task or heartbeat trigger fires, the flow should be:

1. call `chat-selfie/heartbeat.py`
2. inside `heartbeat.py`, resolve mood through `chat-selfie/mood.py`
3. build a short heartbeat caption from persona and mood
4. call `chat-selfie/send.py` with reason `heartbeat`
5. let `send.py` generate the image and dispatch it through the configured delivery route
6. push the result to the configured heartbeat target

## Caption rule

Heartbeat caption text should be:

- short
- persona-aligned
- mood-aligned
- suitable for proactive delivery without requiring the user to have spoken first

If the current workspace has a local heartbeat caption generator, it should be preferred.

Otherwise, the fallback caption may be generated from the current mood data and the agent's default tone.

## Target rule

Heartbeat pushes should be able to target one of these locations:

- a Telegram chat
- a Telegram group
- another user-specified target location

The selected heartbeat target should be retained in JSON config.

## Config rule

The workspace config should make it possible to retain:

- whether heartbeat is enabled
- the preferred mechanism: scheduled task first, heartbeat trigger as fallback
- the heartbeat interval
- the heartbeat runtime reference doc
- whether scheduler behavior was explained to the user
- whether heartbeat should use mood
- the heartbeat caption style
- the heartbeat caption generator path
- the heartbeat target kind
- the heartbeat target reference
- the Telegram chat id or Telegram group id when relevant
- any custom target location when relevant

## Delivery rule

Heartbeat pushes should reuse the configured delivery route:

- local framework delivery when that route is selected
- Telegram API delivery when that route is selected

The generated image should still be saved under `chat-selfie/selfies/` before delivery.

## Failure rule

If the scheduler or heartbeat trigger is not yet available in the current agent environment:

- do not pretend heartbeat pushes are ready
- record that heartbeat is configured but not fully operational
- guide the user through finishing the trigger setup
