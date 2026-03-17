# Reply-time Selfie Flow

## Goal

Define the runtime flow for the `every_reply` mode after Chat Selfie has already been initialized.

This document is not the setup entry point. Use `SKILL.md` first to decide whether the agent should run normal runtime behavior, re-enter setup, or fall back to text-only behavior.

If `delivery.mode = occasional`, use `docs/occasional-delivery.md` instead of forcing this `every_reply` flow.

## When to use this document

Use this flow only when all of these are true:

1. the local `chat-selfie/` workspace already exists
2. `chat-selfie/chat-selfie.json` is present and readable
3. the active delivery mode is `every_reply`
4. the required runtime routes are ready, or the agent has decided how to fall back honestly

If those conditions are not met, the agent should not force this flow.

## Preflight checks

Before following the per-turn steps below, the agent should check:

1. whether `chat-selfie/chat-selfie.json` still reflects the current runtime setup
2. whether mood lookup is enabled and has a usable route
3. whether generation and delivery routes are usable for this turn
4. which delivery route is active: `local_framework` or `telegram_api`
5. whether an existing system capability should be reused before any custom route is considered
6. whether one missing route means the agent should ask for repair setup or continue with text-only behavior

## Base flow

When `delivery mode = every_reply`, one turn should follow this order:

1. the user sends a message
2. the agent receives the message and performs its normal reasoning and task handling
3. before producing the final user-facing reply, the agent prepares the selfie workflow
4. the agent sends the final reply using one of the supported delivery modes

## Pre-reply selfie preparation

Before the final reply is emitted, the agent should:

### 1. Resolve mood

If `agent mood` is enabled:

- prefer an existing system route when one is already working
- otherwise call the configured workspace `chat-selfie/mood.py` route
- prefer a local adapter under `chat-selfie/adapters/` when one exists
- have that wrapper delegate to the fixed repository `mood_resolver` when that is the selected route
- otherwise use another configured implementation that satisfies the mood contract

If `agent mood` is disabled:

- skip mood lookup
- continue with persona and context only

### 2. Build the image prompt

The image prompt should be derived from:

- current persona and identity
- current mood when enabled
- current conversation context
- the intended reply meaning

At minimum, the prompt should include:

- action
- facial expression
- scene or environment
- camera or shooting angle

### 3. Hand off to the delivery adapter

The agent should pass the prepared prompt and any needed reply context to the selected delivery route.

If the selected route is no longer available, do not pretend the handoff succeeded. Instead, either repair setup or continue with a text-only reply.

## Official delivery routes

### A. Local framework route

Use this route when `delivery.route = local_framework`.

The flow should be:

1. resolve mood when enabled
2. generate the image and save it under `chat-selfie/selfies/`
3. hand off the saved image path and final reply text to the current framework
4. let the current framework send both to the user

This remains the default route unless the user chooses another path.

### B. Telegram API route

Use this route when `delivery.route = telegram_api`.

The flow should be:

1. call the workspace `chat-selfie/send.py` entry
2. let that send flow resolve mood internally when needed
3. let that send flow call `chat-selfie/generate.py`
4. save the generated image under `chat-selfie/selfies/`
5. let that send flow call `chat-selfie/send_telegram.py`
6. treat the Telegram photo and caption as the completed final reply for the turn

When the Telegram route succeeds:

- do not send the final reply text again through the current framework
- do not emit a second success message
- do not treat `chat-selfie/mood.py` as a separate user-visible step before `send.py`

## Supported delivery modes

### C. Async send mode

In async send mode:

1. the current chat session continues normally
2. the agent sends the text reply without waiting for image generation to finish
3. image generation runs as an extra operation
4. when the image is ready, it is sent automatically using the configured delivery path

Use this mode when:

- the generation route is slow
- the chat should stay responsive
- image sending can happen after the main reply

### D. Sync send mode

In sync send mode:

1. the agent sends the generated prompt and the final reply payload to the delivery adapter together
2. the adapter waits for generation to finish
3. the adapter sends image and reply together to the user

Use this mode when:

- one bundled send is preferred
- the user experience expects text and image to arrive together

### E. Sync mode using the agent's existing image capability

This is a special sync route where the agent already has a built-in image-generation path.

The flow should be:

1. the agent calls its existing image-generation capability
2. when the image is produced, the agent records the saved image path in local workspace state
3. the agent sends the image and final reply together using the current session's agreed delivery method

At minimum, the agent should record:

- generated image path
- generation timestamp or turn reference
- which route produced the image

## Required local records

When reply-time selfie mode is active, the workspace should make it possible to retain:

- whether the active mode is `every_reply`
- which delivery route is active: `local_framework` or `telegram_api`
- whether mood lookup is enabled
- which delivery mode is active: `async`, `sync`, or `sync_existing_capability`
- which tool or adapter route is used for mood lookup
- which tool or adapter route is used for generation or sending
- the current mood pool path
- the current mood log path

## Rules

- The agent should not skip its normal reasoning just because a selfie is being prepared.
- The selfie prompt should be derived after the agent understands the message, not before.
- Repository-owned tool contracts may guide the process, but user-owned local adapters remain the primary customization point.
- Existing system capabilities should be reused before inventing a new custom route for the same need.
- Generated image output should be saved under `chat-selfie/selfies/` when image generation is enabled.
- If one required route is missing, the agent should either fall back to text-only reply or ask for setup, rather than pretending generation succeeded.
