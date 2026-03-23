# Delivery Contract

## Purpose

Define the minimum contract any Chat Selfie delivery implementation must satisfy.

This contract covers the two official repository-supported delivery paths:

1. local framework delivery
2. Telegram API delivery

## Input shape

A delivery request should be able to carry:

- target destination
- image reference
- caption text
- send reason
- metadata about the active mood or state
- which image source mode is active: real-time generation or fixed mood asset

It should also be possible to carry:

- whether the current route is `local_framework` or `telegram_api`
- whether the image has already been generated and saved locally
- whether the image comes from a pre-existing local mood asset
- whether this route should consume the final reply for the current turn

## Output shape

A delivery result should return at least:

- success or failure
- delivery reference if available
- failure reason if failed

It should also be possible to return:

- whether the current reply was fully consumed by the delivery route
- whether the agent should send any follow-up text after delivery
- the saved image path used for delivery

## Delivery modes

- reply-time send
- occasional send
- heartbeat send

## Heartbeat send

When `delivery mode = heartbeat`, the delivery path is triggered by a scheduled task or another heartbeat-capable trigger rather than a fresh user turn.

The preferred trigger mechanism is:

1. scheduled task
2. heartbeat-capable runtime trigger as fallback

The heartbeat flow should:

1. resolve mood first
2. generate the image
3. generate a short persona-aligned heartbeat caption
4. send image and caption to the configured heartbeat target

The heartbeat target should be configurable, such as:

- Telegram chat
- Telegram group
- another specified target location

## Occasional send

When `delivery mode = occasional`, the delivery path should only trigger when the current turn matches one of the configured occasional triggers.

The default occasional triggers are:

- `new`
- `user_requested`
- `large_task_completed`
- `emotional_conversation`

By default, occasional delivery should also enforce this generation limit:

- one image per agent
- per 15-minute window

If the occasional trigger does not match, or the rate limit is already exhausted, the delivery-related script output should say so clearly in English and should not continue to image generation for that turn.

## Official route A: Local framework delivery

Use this route when the target agent framework can already send an image and the final reply text through its own current session.

The expected behavior is:

1. generate the image first
2. save the generated image under `chat-selfie/selfies/`, or reuse the mood-mapped local asset path when fixed mood-asset mode is enabled
3. hand off the saved image path and final reply text to the current agent framework
4. let that framework deliver the image and text to the user

This is the default route when setup begins, unless the user chooses another path.

## Official route B: Telegram API delivery

Use this route when:

- the current framework cannot reliably send images
- Telegram is configured and approved by the user
- the user prefers the more stable Telegram route

The expected behavior is:

1. call the workspace `chat-selfie/send.py` entry
2. resolve mood inside that send flow when needed
3. resolve the active image source, either by generating a new image or by reusing the local asset mapped to the current mood
4. send the image and final reply text together through Telegram Bot API
5. treat that Telegram send as the completed user-facing reply for the turn

When this route succeeds:

- do not send the final reply text again in the current framework
- do not send a second success notice
- do not separately call a user-visible mood step before `send.py`

## Reply-time selfie handoff

For `reply-time send`, the delivery route should be able to support one of these operational modes:

### 1. Async send

Input should be enough to:

- accept the prepared image prompt
- let the agent continue its normal reply in the current session when the selected route allows that
- generate and send the image after the text reply

### 2. Sync send

Input should be enough to:

- accept the prepared image prompt
- accept the final reply payload
- wait for generation to finish
- send image and reply together

### 3. Sync send using existing image capability

Input should be enough to:

- let the agent use its own existing image-generation capability
- record the generated image location
- send the image and final reply together using the current session's agreed delivery method

## Route-specific rules

### Local framework route

- the saved image should live under `chat-selfie/selfies/`
- the handoff payload should include the saved image path and final text
- if the framework already knows how to send image and text together, reuse it instead of inventing another transport

### Telegram route

- the route should require a saved local image path before send
- the Telegram path should accept final text as caption
- the route should be able to use configured `chat_id`, `bot token`, `api base`, and optional `reply_to_message_id`
- if Telegram delivery succeeds, the turn is already complete

## Failure rule

If one required route is missing or misconfigured:

- do not pretend delivery succeeded
- return a failure or repair-needed result honestly
- allow the agent to re-enter setup or fall back to another supported route
