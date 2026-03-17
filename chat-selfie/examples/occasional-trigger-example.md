# Occasional Trigger Example

## Purpose

This example shows how an agent should decide whether an occasional Chat Selfie send is justified on the current turn.

Use this file as a learning example. The actual rules still live in:

- `docs/occasional-delivery.md`
- `docs/reply-time-selfie-flow.md`

## Core idea

When `delivery.mode = occasional`, the agent should not send on every turn.

A turn should lead to a send only when:

- it matches an allowed occasional trigger
- it is not blocked by the occasional rate limit
- the configured runtime route is actually ready

## Trigger 1: `new`

### Positive example A

Situation:

- the relationship or session is just being established
- this is the first meaningful interaction after setup

Why it counts:

- `new` is meant to allow an initial send when the agent and user establish the session

### Positive example B

Situation:

- the user opens a brand new space for the configured agent
- Chat Selfie is already ready
- no earlier selfie has been sent for this new relationship/session context

Why it counts:

- it is a valid first-send moment

### Not a `new` example

Situation:

- the conversation has already been active for hours
- the agent simply has not sent an image yet

Why it does not count:

- "no image has been sent yet" does not automatically mean the session is still new

## Trigger 2: `user_requested`

### Positive example A

User:
"Send me a selfie."

Why it counts:

- the user explicitly requested the image

### Positive example B

User:
"Show me how you look right now."

Why it counts:

- the intent is still an explicit image request, even if the exact word "selfie" was not used

### Not a `user_requested` example

User:
"You sound cute today."

Why it does not count:

- this is praise, not an image request

## Trigger 3: `large_task_completed`

### Positive example A

Situation:

- the agent finished a substantial implementation, repair, migration, or research task
- the current turn is a real completion moment

Why it counts:

- the task completion is meaningful enough to justify a celebratory or relieved occasional send

### Positive example B

Situation:

- the agent completed a multi-step setup flow and the user now has a working result

Why it counts:

- this is a milestone, not a tiny substep

### Not a `large_task_completed` example

Situation:

- the agent fixed one typo
- the agent answered one routine question
- the agent completed a trivial one-minute change

Why it does not count:

- not every completed action is substantial enough

## Trigger 4: `emotional_conversation`

### Positive example A

User:
"I do not want advice right now. I just want you to stay here with me."

Why it counts:

- the exchange is clearly emotionally meaningful
- the user is inviting presence, not just information

### Positive example B

User:
"I had a really hard day and I do not want to be alone tonight."

Why it counts:

- the emotional weight is explicit
- a carefully aligned selfie can support presence

### Not an `emotional_conversation` example

User:
"Haha, that was funny."

Why it does not count:

- light emotion alone is not enough
- the trigger is meant for emotionally meaningful moments, not every casual positive feeling

## Looks similar, but should not trigger

### Case 1: Friendly small talk

User:
"Morning. Did you sleep well?"

Why it should not trigger:

- warm chat is not automatically an emotional moment
- occasional sends should remain selective

### Case 2: Mild praise

User:
"Nice answer."

Why it should not trigger:

- mild praise alone is usually too small
- save occasional sends for more meaningful moments

### Case 3: Tiny completion

Situation:

- the agent reformatted one paragraph or renamed one variable

Why it should not trigger:

- this is normal activity, not a major completion

## Rate-limit example

### Situation

- the current turn matches `user_requested`
- the workspace already consumed its one-image slot in the active 15-minute window

### Correct behavior

The agent should not behave as if generation is still available.

The user-visible result should clearly say that occasional image generation is currently rate-limited, for example:

- `Occasional image generation is rate-limited for this agent. Please wait 14m 12s before generating another image.`

### Why this is good

- it is honest
- it respects the configured rate gate before generation starts

## Correct skip example

### Situation

- the current turn is ordinary task discussion
- no allowed occasional trigger applies

### Correct behavior

The agent should skip image generation for this turn and continue with normal text behavior.

If the script returns a non-trigger message, it should be clear, for example:

- `Occasional delivery was not triggered for this turn. Allowed triggers: new, user_requested, large_task_completed, emotional_conversation.`

## Decision checklist

Before treating the turn as an occasional send moment, ask:

1. Does this turn match one of the configured occasional triggers?
2. Is the match real, or only superficially similar?
3. Has the occasional rate limit already been consumed in this window?
4. Is the configured generation and delivery route actually ready?

If any answer blocks the send, the agent should not pretend the send is still happening.

## Invalid patterns

- sending on every pleasant turn
- treating any user affection as an image request
- treating any finished action as a large task completion
- ignoring the rate limit because the moment feels special
- forcing a send when the configured route is not actually usable
