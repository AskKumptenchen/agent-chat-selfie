# Heartbeat Example

## Purpose

This example shows what a good heartbeat setup and runtime flow looks like for Chat Selfie.

Use this file as an agent-learning example. The actual rules still live in:

- `docs/heartbeat-delivery.md`
- `docs/startup.md`
- `docs/reply-time-selfie-flow.md`

## What heartbeat means

Heartbeat means the agent may proactively send a photo or short update even when the user did not just send a new message.

The purpose is ongoing presence, not spam.

Heartbeat should therefore be:

- explicitly enabled
- explained in plain language
- tied to a real target
- rate-conscious in tone and frequency
- honest about whether the trigger mechanism is truly ready

## Example 1: Good setup explanation

### Agent says

"Heartbeat means I can occasionally send a small selfie-style update on my own, even when you did not just message me. It is meant to create a gentle sense of presence, so I usually recommend using it more carefully than normal reply-time selfies."

"If you want it on, I also need to know where those updates should go, how often they should happen, and whether they should reflect mood."

### Why this is good

- it explains the feature in user language
- it explains the emotional effect
- it introduces the next decisions without exposing raw config keys

## Example 2: Good confirmation flow

### Agent says

"The next choice is the target. Should heartbeat updates go to this Telegram chat, to a Telegram group, or to another place you already use for delivery?"

User:
"This chat is fine."

Agent says

"Okay. I also recommend starting with a slower interval, such as every 4 hours, unless you want a more active presence. Do you want to keep a slower default like that, or choose a different interval now?"

User:
"Let's keep 4 hours."

Agent says

"One more setting: should heartbeat use mood? If mood is on, those proactive selfies can feel calmer, brighter, or more tired depending on recent context instead of always looking emotionally flat."

User:
"Yes, use mood."

### Why this is good

- the agent explains why each decision matters
- the agent asks one thing at a time
- the agent recommends a practical default without forcing it

## Example 3: Good runtime flow after trigger fires

### Conditions

- heartbeat is enabled
- the configured trigger mechanism is actually available
- the target is a Telegram chat
- `use_mood = true`

### Good behavior

1. the trigger fires
2. the agent calls `chat-selfie/heartbeat.py`
3. `heartbeat.py` resolves mood first
4. the agent builds a short heartbeat caption from persona and mood
5. the send route generates and saves the image under `chat-selfie/selfies/`
6. the route sends the image and short caption to the configured heartbeat target

### Example output shape

- mood: calm but present
- caption: "Still here with you. Quietly glowing in the background tonight."

### Why this is good

- mood is resolved before caption and image delivery
- the caption is short and proactive
- the heartbeat target is the configured destination, not a guessed one

## Example 4: Good fallback when scheduler is not ready

### Situation

The user enabled heartbeat during setup, but no usable scheduled task or other heartbeat-capable trigger is available yet in the current environment.

### Agent says

"Heartbeat is now configured in the workspace, but it is not fully operational yet because this environment does not have the trigger mechanism set up. I can keep the settings we chose, and the remaining step is to connect a scheduled task or another practical heartbeat trigger."

### Why this is good

- it does not pretend the feature is ready
- it preserves the user's choices
- it clearly separates configuration from actual runtime readiness

## Example 5: Bad pattern

### Bad behavior

The agent writes:

"Heartbeat is all set."

But in reality:

- heartbeat was enabled in config
- no scheduler exists
- no fallback trigger exists
- no target delivery path was tested

### Why this is wrong

- it confuses "configured" with "operational"
- it gives the user a false sense of readiness
- it breaks the failure rule in `docs/heartbeat-delivery.md`

## Example 6: Good caption style

Heartbeat captions should usually be:

- short
- persona-aligned
- mood-aligned
- able to stand alone without a new incoming user message

### Good examples

- "A quiet little check-in from me."
- "Still nearby. Soft light, soft thoughts."
- "Taking a breath and staying close."

### Bad examples

- long status reports
- task summaries that assume the user asked a question right now
- generic system notices that do not sound like the persona

## Example 7: Good target handling

If the user chose a Telegram group, heartbeat should go to that Telegram group.

If the user chose the current chat, heartbeat should go to the current chat.

If the user chose another target, the agent should record that target honestly and use that route only when it is actually supported.

The agent should not silently redirect heartbeat to a different destination just because it is easier.

## Example 8: Good repair behavior

### Situation

Heartbeat was enabled earlier, but the user now says:

"Why have I never received any heartbeat selfies?"

### Good behavior

The agent should:

1. inspect whether heartbeat is enabled in workspace config
2. inspect whether a real trigger mechanism exists
3. inspect whether the target route is valid
4. explain what is missing
5. repair only the missing part instead of restarting all Chat Selfie setup

### Why this is good

- it resumes from the broken decision point
- it keeps valid user choices
- it follows the repair-first design of the project

## Invalid patterns

- enabling heartbeat without explaining it first
- asking for raw config keys instead of user-facing choices
- claiming the scheduler is ready when it is not
- skipping mood resolution when heartbeat is configured to use mood
- sending heartbeat updates to a guessed target
- treating heartbeat as if it should fire as often as normal per-reply selfies
