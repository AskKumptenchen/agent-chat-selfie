# Chat Selfie Startup Template

Use this template during startup instead of inventing a new guidance style each time.

The agent may adapt wording to the current persona and language, but should keep the same structure, pacing, and explanation order.

## Core execution rule

- Ask one thing at a time.
- Explain before asking.
- Use non-technical language.
- Give a recommendation when one option is clearly better.
- Do not batch multiple unexplained choices into one message.

## Step 0 — Opening message template

Use an opening like:

- Chat Selfie is installed, and now I will guide you through the setup step by step.
- I will ask one thing at a time, and I will explain what each step means before asking you to choose.
- We will only treat setup as complete when the image generation path is really usable.

Do not open with an internal scope menu unless the user explicitly asked for a compact power-user flow.

## Step 1 — Persona-first template

If the target agent does not already have a clear stable persona, ask this first.

Recommended structure:
1. explain why persona comes first
2. give 2 to 4 easy-to-understand directions
3. allow the user to describe their own version instead

Example structure:
- Before we configure image behavior, we should first decide what kind of presence this agent should have.
- This step decides what kind of assistant or companion it feels like.
- You can pick a direction like: gentle companion / cute assistant / calm professional / describe your own.
- Which one feels closest?

## Step 2 — Portrait template

After persona, explain portrait setup in plain language.

Recommended structure:
- Next we decide what this agent should look like.
- If you already have a reference image, we can use that.
- If image generation is already ready, we can also build the look from a text description.
- If generation is not ready yet, using a reference image is usually the safer path.
- Do you want to upload a reference image, or describe the look in words?

## Step 3 — Generation capability template

This step decides whether Chat Selfie can truly generate images.

Recommended structure:
- Now we need to confirm how it will actually generate images.
- This is the part that decides whether Chat Selfie is truly usable, because persona alone is not enough.
- If generation is still unavailable, setup is not ready yet.
- We can use an existing built-in route, an API route, or a local model route, depending on what is already available.
- Let me help you confirm which path we should use.

If generation is missing, keep guiding here until the generation path is truthfully decided.
Do not jump ahead and call setup ready.

If the user chooses fixed mood-asset mode instead of real-time generation, switch to a collection step:
- explain that the agent can collect the mood images directly in chat
- ask the user to send the images one by one or as a small batch
- save them into the local workspace, such as `chat-selfie/stickers/`
- record each saved file back into the matching mood entry through `asset_path`
- only call the mood-asset setup ready after the saved files are actually present

## Step 4 — Delivery frequency template

Explain this before asking.

Recommended structure:
- Next we decide how often the agent should send selfies in chat.
- If it sends one on every reply, the presence feels strongest, but the cost is higher because it has to generate an image each time.
- If it sends only at suitable moments, the cost is lower and this is usually a safer default.
- If it only uses heartbeat pushes, it will mainly appear through proactive moments instead of normal replies.
- If you are still in testing, I usually recommend occasional sends first.
- Which style do you want?

## Step 5 — Delivery route template

Explain what this step controls.

Recommended structure:
- Now we decide which sending path to use.
- One path is the current local framework route.
- The other is a Telegram route, which is often more stable when image sending is unreliable.
- If you want the simpler default first, we can try the local route.
- If you want the more stable route for image delivery, Telegram is usually safer.
- Which one should we use?

## Step 6 — Mood template

Explain mood before asking.

Recommended structure:
- Next we decide whether the selfies should change expression and state based on the mood of the conversation.
- If mood is enabled, each generated image can carry a more fitting emotion, expression, and state based on the current context, so the agent feels more alive and less flat.
- In plain terms, it means the pictures will not all look emotionally the same. They can look shy, calm, playful, tired, clingy, happy, or otherwise match the moment more naturally.
- If mood is disabled, the setup is simpler, but the emotional expression of the images will feel flatter.
- In most cases, I recommend turning mood on, because emotional variation is one of the core parts of Chat Selfie.
- Do you want mood on or off?

If mood is enabled, then ask a follow-up:
- Should mood mainly follow preset styles, or should it follow the conversation context more dynamically?

## Step 7 — Heartbeat template

Explain heartbeat before asking.

Recommended structure:
- Now we decide whether the agent should sometimes reach out on its own.
- Heartbeat means it can proactively send a photo or short update even when you did not just message it.
- This is meant to create a stronger feeling of ongoing presence.
- If you want something more restrained at first, we can leave it off and add it later.
- Do you want heartbeat on or off?

If heartbeat is enabled, ask follow-ups one by one:
- where should those pushes go?
- should we keep the default interval, or change it?

## Step 8 — Completion template

At the end, summarize in plain language:
- what is now decided
- what is still missing
- whether image generation is truly available
- whether Chat Selfie is ready or still not ready
- what the next guided step is, if anything is still missing

Use a completion style like:
- We have now finished the setup choices for persona, portrait, generation path, sending style, mood, and heartbeat.
- Image generation is available / still not available.
- So Chat Selfie is ready / not ready yet.
- If not ready, the next thing we need to finish is: ...

## Strict prohibitions

Do not do these during startup:
- do not ask 4 unrelated decisions in one message without explanation
- do not ask the user to answer in compressed codes like 1B 2A 3A 4B unless the user explicitly asked for a compact mode
- do not say mood, heartbeat, occasional, or delivery route without explaining them first
- do not call setup ready when image generation is still unavailable
- do not replace guided interaction with a fake minimal initialization
