# Mood Tool Contract

Use this contract when Chat Selfie needs the current mood or emotional state for one target agent.

The intended structure is:

- a fixed repository-owned `mood_resolver.py`
- a workspace-local `chat-selfie/mood.py` wrapper
- a workspace-local `chat-selfie/mood-pool.json`
- a workspace-local `chat-selfie/chat-selfie.json`
- a workspace-local `chat-selfie/mood-log.jsonl`

## Expected output

A mood tool result should provide:

- mood id
- human-readable label
- reply-style prompt
- state hint
- optional camera prompt
- optional expression prompt
- optional scene prompt
- optional action prompt
- source: `explicit` | `recent` | `random`

## Allowed implementation routes

- the workspace `chat-selfie/mood.py` wrapper calling the fixed resolver
- an existing system route
- a local adapter under `chat-selfie/adapters/`
- another user-provided custom route

## Fixed resolver inputs

The repository-owned resolver should accept:

1. mood pool json path
2. current agent id
3. optional explicit mood id
4. `chat-selfie` config path

## Resolution logic

### 1. Explicit mood

If a mood id is passed:

- resolve that mood directly
- return the reply-style prompt
- if prompt-part generation is enabled, randomly choose at least one `camera`, `expression`, `scene`, and `action` value
- record the call in `chat-selfie/mood-log.jsonl`

### 2. Direct call without mood id

If no mood id is passed:

- if the same agent has a recorded mood inside the configured reuse window, reuse it
- otherwise pick a mood from the configured pool and save it for later reuse

## Rule

This contract does not force one fixed persona vocabulary.
It defines the fixed resolver boundary and the expected workspace files.
