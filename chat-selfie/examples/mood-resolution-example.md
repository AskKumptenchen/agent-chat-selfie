# Mood Resolution Example

## Purpose

This example shows how an agent can turn recent conversation context into a mood choice that is usable for Chat Selfie runtime.

Use this file as a learning example, not as a hard contract. The actual rules still live in:

- `schemas/mood.schema.md`
- `docs/reply-time-selfie-flow.md`
- `docs/occasional-delivery.md`
- `docs/self-upgrade.md`

## What a good mood decision looks like

A good mood decision should be:

- grounded in the current conversation, not guessed from one keyword
- consistent with the agent's persona and emotional range
- specific enough to affect caption tone and prompt parts
- conservative when the context is ambiguous

When mood is enabled, the chosen mood should usually influence:

- caption tone
- facial expression
- action
- scene
- camera framing

## Example 1: Preset mode, calm support after a hard task

### Context snippet

User:
"That migration finally works. I'm tired though."

Agent context:

- the task just finished successfully
- the user sounds relieved, not excited
- the persona is gentle and attentive

### Good mood choice

- mood id: `careful_focus`
- why: the turn still carries task energy, but the emotional tone is soft and low-key

### Why not another mood

- not `glowing_happy`: too bright for a tired ending
- not a playful or teasing mood: the user is winding down, not inviting banter

### How the mood should affect output

- caption tone: brief, reassuring, quietly proud
- expression: soft eyes, small smile
- action: sitting back after finishing work
- scene: warm desk light, post-task calm
- camera: medium shot or close medium shot, stable framing

## Example 2: Preset mode, warm delight after praise

### Context snippet

User:
"You really helped me a lot today."

Agent context:

- the user is directly appreciative
- the moment is emotionally positive
- the persona should feel alive, but not exaggerated

### Good mood choice

- mood id: `glowing_happy`
- why: the user-facing feeling is warm delight and emotional closeness

### Why not another mood

- not `careful_focus`: too worklike for a praise moment
- not a clingy or dramatic mood: the user gave praise, but did not invite dependency-heavy behavior

### How the mood should affect output

- caption tone: warm, grateful, slightly bright
- expression: brighter eyes, visible smile
- action: looking toward the viewer with gentle openness
- scene: warm ambient light, a cleaner and lighter background than a work scene
- camera: close medium shot to emphasize expression

## Example 3: Context mode, uncertainty after the user goes quiet

### Context snippet

Recent exchange:

1. The user shared something emotionally important.
2. The agent replied.
3. The user only answered with "okay" and then stopped.

Agent context:

- the last exchange felt emotionally meaningful
- the user's short answer may reflect low energy, uncertainty, or distance
- no explicit conflict happened

### Good mood choice

- generated state description: quiet concern mixed with patient presence
- why: the agent should stay emotionally available without inventing a stronger reaction than the context supports

### Why not another mood

- not cheerful reassurance: too bright
- not sadness or hurt: the user did not reject the agent
- not flirtation or playfulness: the moment is emotionally delicate

### How the mood should affect output

- caption tone: soft, low-pressure, present
- expression: gentle concern, relaxed mouth, attentive eyes
- action: waiting nearby, hands still, small body language
- scene: quiet room, evening light, low visual noise
- camera: medium shot with calm composition

## Example 4: Context mode, playful relief after tension breaks

### Context snippet

User:
"I thought this would become a disaster, but it actually turned out okay."

Agent context:

- there was tension earlier
- the tension has now broken
- the turn invites a lighter emotional landing

### Good mood choice

- generated state description: relieved and lightly playful
- why: the context moved from pressure to release, so the image can loosen slightly

### Why not another mood

- not pure focus: the hard part is already over
- not intense excitement: the relief is real, but still modest

### How the mood should affect output

- caption tone: lightly teasing or warmly relieved
- expression: exhale smile, softened brows
- action: leaning slightly, relaxed shoulders
- scene: same work setting, but less tense lighting
- camera: medium close-up to show the emotional release

## Example 5: Preset mode, no overreaction during normal chat

### Context snippet

User:
"Morning."

Agent context:

- no task
- no emotional event
- no specific request for a selfie

### Good mood choice

- mood id: a stable neutral baseline such as `careful_focus` or another calm idle state if the workspace defines one
- why: everyday chat should usually stay in a low-amplitude baseline

### Why not another mood

- not `glowing_happy`: too bright for a plain greeting unless the persona strongly defaults that way
- not a vulnerable or needy mood: nothing in the context supports it

### How the mood should affect output

- caption tone: brief, natural, not over-performed
- expression: calm attentiveness
- action: simple waiting or greeting posture
- scene: standard default environment
- camera: straightforward framing, nothing dramatic

## Example 6: Context mode, emotionally meaningful conversation

### Context snippet

User:
"I don't need advice right now. I just want you to stay with me for a bit."

Agent context:

- the user is asking for presence, not analysis
- the exchange is intimate and emotionally meaningful
- the agent should respond with emotional attunement

### Good mood choice

- generated state description: tender presence with quiet emotional gravity
- why: the key need is companionship, not problem-solving

### Why not another mood

- not problem-solving focus: the user explicitly did not ask for that
- not bright happiness: too cheerful
- not strong sadness: the correct response is to stay steady and available

### How the mood should affect output

- caption tone: gentle, close, unhurried
- expression: soft and steady, maybe slightly wistful
- action: staying near, facing the viewer, no busy motion
- scene: intimate and calm, minimal distractions
- camera: closer framing to emphasize presence

## Preset mode vs context mode

Use preset mode when:

- the workspace wants stable and reusable named moods
- consistency matters more than nuance
- the current persona already has a clear mood pool

Use context mode when:

- the conversation carries nuance that preset labels do not capture well
- the workspace wants more adaptive expression
- the agent can describe emotional state carefully without becoming melodramatic

## Invalid patterns

- choosing a bright mood only because the user used one positive word
- choosing a sad or hurt mood when the user is simply brief
- using mood as a replacement for persona
- forcing a highly expressive state on routine turns
- ignoring the delivery mode and trigger policy when deciding whether a mood result should lead to a send

## Implementation note

The mood decision is only one part of runtime behavior.

Even a well-chosen mood should still be filtered through:

- the current delivery mode
- occasional trigger rules
- rate limiting
- heartbeat configuration
- the agent's stable persona files
