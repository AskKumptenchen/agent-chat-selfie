# Startup Conversation Example

## Purpose

This example shows what a guided-first Chat Selfie setup conversation should sound like.

Use this file as a conversation example, not as the canonical rule source. The actual startup contract still lives in:

- `docs/startup.md`
- `docs/integration.md`
- `docs/workspace-layout.md`

## What good startup behavior looks like

During startup, the agent should:

- guide the user step by step
- explain why each decision matters before asking for it
- ask one important question at a time by default
- confirm major branch choices before moving on
- treat `continue` as permission to continue the guided setup, not as permission for autonomous multi-phase implementation

## Example 1: Standard guided onboarding

### User

"Help me set up Chat Selfie."

### Agent

"I can guide you through that step by step. First I need to understand which agent we are configuring, because the selfie behavior should attach to that agent's existing persona rather than replacing it."

"Which agent should Chat Selfie be set up for?"

### User

"The current agent."

### Agent

"Good. The next thing that matters is whether this agent already has a stable persona. Chat Selfie works best when it reflects an existing emotional tone instead of inventing one from scratch."

"Does the current agent already have a clear persona and relationship style, or should we define that first?"

### User

"It already does."

### Agent

"Great. Then the next practical choice is the portrait source. I ask this early because a saved reference image and a text-generated portrait have different setup needs."

"Do you want to start from a saved reference image, or from a text-generated base portrait?"

### User

"A saved reference image."

### Agent

"That is the safest starting path. Before we talk about generated portraits, I also need to know whether this environment already has a working image-generation route. If it does, Chat Selfie should reuse it instead of forcing a new provider."

"Do we already have a working image-generation route for this agent?"

### User

"Yes."

### Agent

"Good. Then I can keep setup focused on delivery and behavior rather than backend repair."

"The next choice is when selfies should appear. The simplest first setup is usually occasional sends instead of sending one on every reply."

"Do you want occasional sends, or selfies on every reply?"

### User

"Occasional."

### Agent

"Okay. In occasional mode, Chat Selfie does not send on every turn. By default it only sends on selected moments, such as a direct user request, a meaningful emotional moment, or the completion of a substantial task. There is also a default rate limit so it does not send too often."

"Do you want to keep that kind of occasional behavior, or customize the trigger policy right away?"

### User

"Keep the default."

### Agent

"Next is the delivery route. The default path is local framework delivery, but Telegram is often more reliable when image sending is unstable. I want to explain the tradeoff before you choose."

"Would you like to use the local framework route, or the Telegram API route?"

### User

"Telegram."

### Agent

"Understood. I will treat Telegram as the active route, and I will also retain that it was explicitly chosen."

"One more feature to decide is heartbeat. Heartbeat means the agent can proactively send a small selfie-style update even when you did not just message first. It creates presence, so it is usually used more carefully than reply-time sends."

"Do you want heartbeat enabled?"

### User

"Not yet."

### Agent

"Last core choice: mood. Mood means the same character can look calm, shy, bright, tired, or otherwise more emotionally fitting to the moment instead of always feeling flat. I usually recommend enabling it."

"Do you want mood enabled?"

### User

"Yes."

### Agent

"Then I need one final mood choice. Preset-driven mood is more stable and easier to control. Context-driven mood is more adaptive and expressive, but a bit less predictable."

"Which one do you want to start with?"

### User

"Preset."

### Agent

"Perfect. I now have the main branch decisions. I can move on to writing the workspace artifacts and runtime references for this setup, including `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and `chat-selfie/send-flow.md`."

## Example 2: Good follow-up when the answer is too vague

### User

"Just make it cute."

### Bad response

"Okay, I will configure everything."

### Why this is bad

- it treats a vague preference as full setup authorization
- it skips the blocking decision that still matters

### Good response

"I can work with that direction, but I still need one concrete choice before setup can continue. The immediate blocking step is the portrait source, because a saved reference image and a generated portrait require different setup paths."

"Do you want to upload a saved reference image, or should this start from a text-generated base portrait?"

## Example 3: Good handling of `continue`

### Prior context

The agent just explained the difference between local framework delivery and Telegram delivery.

### User

"Continue."

### Correct interpretation

The agent should continue to the next guided setup question, not silently choose a route and continue implementing multiple later phases on its own.

### Good response

"The next step is to choose the delivery route. The default is local framework delivery, while Telegram is often more reliable when image sending is unstable."

"Which route do you want to use right now?"

## Example 4: Good persona-first recovery when persona is missing

### Situation

The user asks for Chat Selfie setup, but the target agent does not have a stable persona yet.

### Good response

"Before I can set up selfie behavior, I need to anchor who this agent is supposed to feel like. Chat Selfie should reflect an existing persona, not invent one blindly."

"What kind of assistant or companion should this agent feel like in everyday interaction?"

### Why this is good

- it follows the persona-first rule
- it asks in ordinary language
- it does not expose raw internal config terms

## Example 5: Good summary after a setup step

After a meaningful setup step, a good summary should sound like this:

"So far we have confirmed the target agent, the portrait source, the existing generation route, occasional delivery, Telegram delivery, and preset mood. Heartbeat is still off. The next step is to write `SOUL.md`, `AGENTS.md`, `TOOLS.md`, `chat-selfie/send-flow.md`, and the structured workspace records, then run the final review checklist."

This is better than milestone language such as:

- "Phase one complete"
- "Proceeding autonomously to the next implementation stage"

## Example 6: Good final review explanation

After startup writing work is done, a good final review explanation should sound like this:

"Before I can mark Chat Selfie as usable, I need to run the final review checklist. That means checking that `SOUL.md`, `AGENTS.md`, `TOOLS.md`, `chat-selfie/send-flow.md`, and the workspace records all exist, match the setup we just confirmed, and point to real usable routes."

"That checklist also has to cover every other setup item we decided during startup, such as delivery frequency, occasional triggers, heartbeat settings, mood mode, portrait path, and route readiness. If we configured it, the final review has to verify it."

"If one required file is still missing, or if a configured route still does not pass honest preflight, the correct result is not 'ready enough'. I have to keep the workspace in setup or repair mode until that is fixed."

## Invalid patterns

- starting with a broad internal scope menu when a more immediate prerequisite is missing
- asking for raw JSON by default
- asking many branch questions at once before explaining them
- treating `continue` as permission for autonomous development
- claiming setup is complete before the blocking generation or delivery route is actually ready
