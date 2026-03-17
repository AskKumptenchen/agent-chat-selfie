# Occasional Delivery

## Goal

Define how Chat Selfie should behave when `delivery.mode = occasional`.

In this mode, the agent should not try to generate and send an image on every turn.

## Default trigger policy

By default, occasional delivery should allow these triggers:

- `new`
- `user_requested`
- `large_task_completed`
- `emotional_conversation`

The intended meaning is:

- `new`: allow one initial send when the relationship or session is first established
- `user_requested`: the user explicitly asks for an image or selfie
- `large_task_completed`: a substantial task or milestone has just been completed
- `emotional_conversation`: the current context is emotionally meaningful enough to justify a selfie

If the current turn does not match one of the configured occasional triggers, the agent should skip image generation for that turn.

## Default rate limit

When `delivery.mode = occasional`, the default generation limit is:

- one image per agent
- per 15-minute window

This limit should apply before image generation starts.

## Rate-limit scope

The rate-limit gate should protect scripts that may be used immediately before generation, including:

- `chat-selfie/mood.py`
- `chat-selfie/send.py`

If one of those scripts consumes the occasional generation slot, a second generate-intended call inside the same window should not continue as if generation were still available.

## Rate-limit response

If the agent hits the occasional rate limit, the script output should clearly say so in English.

For example:

- `Occasional image generation is rate-limited for this agent. Please wait 14m 12s before generating another image.`

If the current turn simply does not match an allowed occasional trigger, the output should also say so clearly in English.

For example:

- `Occasional delivery was not triggered for this turn. Allowed triggers: new, user_requested, large_task_completed, emotional_conversation.`

## Initialization rule

During setup, the agent should:

1. explain that occasional mode does not send on every turn
2. explain the default occasional triggers
3. explain the default 15-minute, one-image rate limit
4. tell the user that both the time window and the allowed image count can be changed
5. ask whether the user wants to keep the default values or customize them

## Config rule

The workspace config should make it possible to retain:

- the occasional trigger list
- the occasional rate-limit window in minutes
- the maximum image count allowed in that window
- the occasional rate-limit record path
- whether the rate limit was explained to the user
- whether the user approved custom values or kept the default values
