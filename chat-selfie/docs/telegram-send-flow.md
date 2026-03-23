# Telegram Send Flow

## Goal

Define the official Telegram API delivery path for Chat Selfie when the target agent cannot reliably send images through its current framework, or when the user explicitly prefers the Telegram route.

## When to use this flow

Use this flow when all of these are true:

1. the user has agreed to use the Telegram route
2. `delivery.route = telegram_api`
3. Telegram chat target and bot token configuration are ready
4. the active image source can provide a usable local image file, either from generation or from a mood-mapped asset

This route is more stable than relying on every agent framework to support image sending in-session, but it requires Telegram-specific configuration.

## Entry rule

For the Telegram route, the current turn should call the workspace `chat-selfie/send.py` entry directly.

Do not call `chat-selfie/mood.py` as a separate user-visible step first.

Instead, pass:

- the target agent id
- the final reply text for this turn
- the mood id when one is already known for this turn

If no explicit mood id is passed, `send.py` should resolve mood internally through the configured workspace mood route.

## Flow

The Telegram route should follow this order:

1. call `chat-selfie/send.py`
2. inside `send.py`, resolve mood through `chat-selfie/mood.py` when mood is enabled or an explicit mood id is provided
3. inside `send.py`, call `chat-selfie/generate.py`
4. `generate.py` either produces one saved image under `chat-selfie/selfies/` or returns the local image already mapped to the resolved mood
5. inside `send.py`, call `chat-selfie/send_telegram.py`
6. `send_telegram.py` sends the image and the final reply text together through Telegram Bot API
7. once Telegram sending succeeds, the current reply is considered finished

## Completion rule

When the Telegram route is used successfully:

- do not send the final reply text again through the current agent framework
- do not emit a second text-only reply to the user
- do not emit a separate "send succeeded" confirmation message

The Telegram photo and caption already count as the completed user-facing reply for that turn.

## Required configuration

The workspace config should make it possible to resolve:

- `workspace.selfies_path`
- `workspace.send_tool_path`
- `workspace.generate_tool_path`
- `workspace.telegram_send_tool_path`
- `delivery.route`
- `generation.image_source`
- `delivery.telegram.chat_id` or `delivery.telegram.chat_id_env`
- `delivery.telegram.bot_token_env`
- `delivery.telegram.api_base_env`
- `delivery.telegram.parse_mode`
- `delivery.telegram.consume_final_reply`

When `generation.image_source = mood_asset`, the workspace should also make it possible to resolve the current mood entry and its `asset_path`.

## Image path rule

When real-time image generation is enabled for the Telegram route, the generated image should be saved under `chat-selfie/selfies/`.

The generation step should not save output into unrelated temporary folders unless it then moves or copies the final deliverable into `chat-selfie/selfies/` before Telegram delivery.

When fixed mood-asset mode is enabled, Telegram delivery may reuse the mapped local asset path directly instead of generating a new file for that turn.

## Failure rule

If one required part is missing:

- missing Telegram configuration: ask the user to finish Telegram setup
- missing generation route in real-time mode: repair generation setup before using Telegram delivery
- missing mood asset path in fixed mood-asset mode: repair the mood asset mapping before using Telegram delivery
- missing saved image path: do not pretend Telegram delivery succeeded

If the Telegram route cannot complete honestly, the agent should either:

1. re-enter repair setup, or
2. switch back to the local framework route after explaining the limitation to the user

Before restarting guided setup, the runtime should first consult `docs/self-repair.md` to decide whether the problem can be auto-repaired, retried without `parse_mode`, or degraded to another honest route.
