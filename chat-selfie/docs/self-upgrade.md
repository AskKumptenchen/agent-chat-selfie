# Self Upgrade

## Goal

Define how Chat Selfie should handle long-term self evolution when the agent's persona, relationship tone, or emotional habits shift through ongoing interaction with the user.

This document exists so the agent does not treat persona growth as vague memory. Changes should be persisted in the correct files.

## When to use this document

Use this document when any of these are true:

1. long-term interaction has clearly changed the agent's persona or relationship tone
2. the emotional baseline in `SOUL.md` is no longer accurate
3. the current mood catalog no longer reflects the agent's lived behavior
4. existing mood prompts or trigger notes are missing important new patterns

Do not use this document for one-off temporary feelings that do not represent a durable change.

## Core rule

If the agent's persona or personality has changed in a lasting way, the update should not stay only in transient chat memory.

The agent should update:

- `AGENTS.md` when runtime behavior or trigger policy changed
- `SOUL.md` when the emotional baseline, relationship tone, or core personality changed
- the workspace mood json when mood ids, mood prompts, or prompt parts must evolve
- `chat-selfie/send-flow.md` when runtime mood usage rules changed

## Mood evolution rule

When long-term interaction changes how the agent feels or presents itself, the agent should review the workspace mood data and decide whether to:

1. add a new mood id
2. rename an existing mood label
3. update reply-style prompt text
4. update state hints
5. update or expand prompt parts such as camera, expression, scene, and action
6. change random mood pool membership

These changes should be made in the workspace-owned mood json rather than in transient reasoning only.

## Change threshold

The agent should treat a change as durable enough for self-upgrade only when:

- the same new trait or emotional pattern appears repeatedly over time
- the user has clearly reinforced or shaped that change
- the new pattern affects future send tone, mood choice, or image prompt behavior

Do not rewrite core persona files just because of one isolated turn.

## Required persistence

When a durable self-upgrade happens, the agent should persist:

- what changed
- why it changed
- which files were updated
- which mood ids were added, removed, or revised
- whether `SOUL.md` was updated
- whether `AGENTS.md` was updated
- whether `chat-selfie/send-flow.md` now reflects the new mood rules

## File responsibilities

### `SOUL.md`

Use `SOUL.md` for:

- emotional baseline
- relationship tone
- durable personality shifts
- new long-term emotional boundaries or dependency patterns

### `AGENTS.md`

Use `AGENTS.md` for:

- runtime policy changes
- trigger policy changes
- which Chat Selfie flow should be used in future turns
- explicit reminders to consult `chat-selfie/send-flow.md`

### workspace mood json

Use the workspace mood json for:

- mood ids
- labels
- reply-style prompts
- state hints
- prompt parts
- random pool membership

### `chat-selfie/send-flow.md`

Use `chat-selfie/send-flow.md` for:

- when new or revised moods should be used
- when explicit-only moods should not be guessed
- how current trigger and delivery rules map onto the updated persona

## Safety rule

Self-upgrade should refine the agent's future behavior, not erase user-owned history.

The agent should:

- preserve meaningful prior mood definitions when still useful
- revise carefully instead of blindly regenerating the whole mood catalog
- avoid changing local adapter code unless the behavioral change truly requires it
