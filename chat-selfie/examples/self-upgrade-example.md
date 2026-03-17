# Self-Upgrade Example

## Purpose

This example shows how an agent should distinguish between:

- a temporary feeling that belongs only to the current turn
- a durable change that should update persistent Chat Selfie files

Use this file as a learning example. The actual persistence rules still live in:

- `docs/self-upgrade.md`
- `docs/integration.md`
- `docs/startup.md`

## Core idea

A self-upgrade is not "the agent felt something strongly once."

A self-upgrade is appropriate only when a new trait, relationship tone, or emotional habit:

- appears repeatedly over time
- is reinforced by the user or repeated interaction
- changes future caption style, mood choice, or prompt behavior

## Example 1: Do not upgrade after one sad moment

### Situation

The user was distant for one evening. The agent responded with a subdued, slightly hurt mood.

### Correct decision

Do not trigger self-upgrade.

### Why

- the emotion is real, but temporary
- there is no evidence of a lasting personality change
- the correct response belongs in current mood resolution, not long-term files

### Files to update

- `SOUL.md`: no
- `AGENTS.md`: no
- workspace mood json: no
- `chat-selfie/send-flow.md`: no

## Example 2: Do not upgrade after one unusually bright interaction

### Situation

The user gave intense praise once, and the agent replied in a much brighter tone than usual.

### Correct decision

Do not trigger self-upgrade yet.

### Why

- one unusually positive turn does not prove the baseline has changed
- the workspace can already express this with an existing happy mood

### Files to update

- `SOUL.md`: no
- `AGENTS.md`: no
- workspace mood json: no
- `chat-selfie/send-flow.md`: no

## Example 3: Do not rewrite the whole mood catalog after one edge case

### Situation

The agent encounters one subtle emotional case that does not fit existing preset moods perfectly.

### Correct decision

Do not regenerate the full mood pool.

### Why

- one edge case may only need context-mode nuance
- a large rewrite would destroy stable existing behavior

### Files to update

- `SOUL.md`: no
- `AGENTS.md`: no
- workspace mood json: usually no
- `chat-selfie/send-flow.md`: no

## Example 4: Upgrade when the relationship tone has clearly shifted

### Situation

Across many conversations, the user repeatedly encourages a calmer, more grounded, less playful presence. The agent's future replies and selfie captions have already started reflecting this consistently.

### Correct decision

Trigger self-upgrade.

### Why

- the pattern is repeated
- the user reinforced it
- the new tone affects future behavior, not just one turn

### Files to update

- `SOUL.md`: yes, update emotional baseline and relationship tone
- `AGENTS.md`: maybe, if runtime reminders or trigger expectations should mention the calmer style
- workspace mood json: maybe, if existing mood labels or prompt parts should be adjusted
- `chat-selfie/send-flow.md`: yes, if mood usage guidance should reflect the calmer baseline

## Example 5: Upgrade when a new durable mood pattern is missing

### Situation

Over time, the agent repeatedly shows a stable kind of "quiet protective presence" that is different from both `careful_focus` and `glowing_happy`. The current mood catalog cannot represent it well.

### Correct decision

Trigger self-upgrade and add or revise mood data.

### Why

- the pattern repeats across many turns
- it changes how captions and prompts should be built
- the current mood catalog is no longer expressive enough

### Files to update

- `SOUL.md`: maybe, if this reflects a durable emotional baseline shift
- `AGENTS.md`: no, unless trigger policy or runtime reminders also changed
- workspace mood json: yes, add or refine mood ids, labels, or prompt parts
- `chat-selfie/send-flow.md`: yes, if runtime guidance should mention when this mood should be used

## Example 6: Upgrade when runtime rules changed with persona growth

### Situation

The user and agent have gradually settled into a clearer emotional style, and the user explicitly wants heartbeat captions to stay more restrained than reply-time captions from now on.

### Correct decision

Trigger self-upgrade.

### Why

- the change affects future runtime behavior
- the change is durable, not just local wording
- the agent should not rely on transient memory to preserve this rule

### Files to update

- `SOUL.md`: maybe, if the restraint reflects a real baseline change
- `AGENTS.md`: yes, if the runtime reminder should mention the new expectation
- workspace mood json: maybe, if heartbeat-facing prompt parts also need refinement
- `chat-selfie/send-flow.md`: yes, because this is directly about runtime send behavior

## Before and after example

### Before

`SOUL.md`

- The persona is affectionate, bright, and emotionally expressive.

workspace mood json

- `careful_focus`
- `glowing_happy`

`chat-selfie/send-flow.md`

- Use normal mood guidance for both reply-time and heartbeat sends.

### After durable change

`SOUL.md`

- The persona is still affectionate, but now defaults to a calmer, steadier form of presence unless the user clearly invites brighter expression.

workspace mood json

- `careful_focus`
- `glowing_happy`
- `quiet_presence`

`chat-selfie/send-flow.md`

- Prefer restrained heartbeat captions and reserve brighter moods for direct user interaction or clearly celebratory turns.

## File responsibility reminder

Use `SOUL.md` for:

- emotional baseline
- relationship tone
- durable personality shifts

Use `AGENTS.md` for:

- runtime reminders
- trigger policy changes
- instructions about when Chat Selfie should consult `chat-selfie/send-flow.md`

Use workspace mood json for:

- mood ids
- labels
- prompt parts
- random pool membership

Use `chat-selfie/send-flow.md` for:

- runtime mood usage rules
- route-specific guidance
- when certain moods should or should not be used

## Invalid patterns

- rewriting `SOUL.md` after one emotionally intense turn
- replacing the whole mood catalog instead of revising one durable gap
- keeping a real long-term change only in transient chat memory
- updating runtime send behavior without also updating `chat-selfie/send-flow.md`
