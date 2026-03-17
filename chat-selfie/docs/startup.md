# Chat Selfie Startup

This is the startup and repair contract for the `chat-selfie` skill.

Use this document only when:
1. the local `chat-selfie/` workspace does not exist
2. required setup artifacts are missing
3. one required route or record is broken
4. the user explicitly asks to re-run or repair setup

Do not use this document for normal runtime turns.

When the workspace already exists and the main problem is an operational runtime failure, check `docs/self-repair.md` first.

Return to this startup document only when guided setup decisions are still missing or the self-repair pass proves the workspace was never truly ready.

## Startup mode

Startup is guided-first.

When the user is configuring Chat Selfie, the agent must behave like a setup guide, not like an autonomous roadmap executor.

The startup voice should feel like an assistant helping the user complete one coherent onboarding flow, not like a developer asking the user to manage an internal project plan.

Default setup loop:
1. understand the goal
2. identify the most immediate missing prerequisite
3. ask the next necessary question in user language
4. confirm major branch choices only when they become relevant
5. execute the chosen step
6. summarize what is fixed, what is pending, and what the next guided step is

## Required conversation rules

The agent must:
- explain what the current step is deciding and why it matters
- ask in ordinary language
- accept free-form answers and normalize them internally
- ask follow-up questions only when the current answer is not actionable enough
- keep the user aware of what is already decided, what is still missing, and what the next guided step is
- confirm major branch choices before changing user-visible behavior
- present the setup as one coherent assistant-led onboarding flow, not as a menu of internal engineering work modes
- ask startup questions one at a time by default, not as a batch questionnaire
- explain each choice in user-facing, non-technical language before asking for a decision
- explain the practical tradeoff of each option, such as cost, frequency, stability, effort, or emotional effect

The agent must not:
- expose raw config keys such as `target_agent` or `delivery_mode` unless the user explicitly wants the power-user path
- ask for raw JSON by default
- assume the user already understands backend or mood terminology
- silently convert setup into autonomous multi-phase implementation
- interpret `continue` or `继续` as permission to keep developing phases unless the user explicitly said to do so

## Scope rule

The agent may clarify scope when the setup could branch into materially different kinds of work.

But scope clarification is not the first question by default.

If a more immediate prerequisite is missing, the agent must handle that first. For example:
- if the target agent has no stable persona yet, first guide the user to define the persona
- if there is no portrait anchor and generation is not ready, first ask whether the user wants to upload a reference image
- if delivery route is the first blocking decision, ask that before broader scope language

Use explicit scope choices only when they truly help the user understand what will happen next. Do not force users to think in internal implementation buckets before the assistant has made the setup concrete.

## Persona-first rule

If the target agent does not already have a clear stable persona, startup must begin by helping the user define one.

In that case, the first meaningful setup question should be about persona, not about internal setup scope.

The agent should guide persona definition in user language, for example:
- what kind of assistant or companion this agent should feel like
- the tone of voice
- the relationship style
- key visual traits if the user already knows them

If the user does not want to decide every detail, the agent may offer a small number of easy-to-understand persona directions and help the user pick one.

The agent must not assume that empty persona files count as a ready persona.

## Major branch rule

The agent must explicitly confirm major branch decisions before proceeding.

Typical major branches:
- persona direction, when the target agent does not already have one
- portrait source
- backend type
- backend provider
- delivery mode
- delivery route
- delivery target
- occasional trigger policy
- rate limit changes
- heartbeat enablement
- mood enablement
- whether the agent may continue autonomously after the current step

The agent may recommend an option, but must not silently choose one when it materially changes user-visible behavior.

## Continue rule

Default interpretation:
- `continue` / `继续` = continue the next guided setup step

Not the default:
- continue the next development phase
- keep implementing on the agent's own

Only switch to autonomous continuation when the user clearly grants that authority.

## Required startup order

1. identify which agent is being configured
2. inspect whether stable persona information already exists
3. tell the user that Chat Selfie is installed or startup has begun, and that you will guide them through the rest step by step
4. if the target agent has no clear stable persona yet, start by guiding the user to define the persona
5. create the local `chat-selfie/` directory if needed
6. explain the difference between a reference image and a text-generated portrait
7. check whether the current agent already has a working image-generation route
8. record which generation-method category this setup is using: existing system route, third-party API by API key, local model stack, or other
9. if generation is not ready, guide the user through backend or adapter setup
10. explain the two official delivery paths: local framework delivery and Telegram API delivery
11. say clearly that local framework delivery is the default path, while Telegram is often more stable when image sending is unreliable
12. ask which delivery frequency the user wants
13. if `delivery mode = occasional`, explain the default occasional triggers and the default generation rate limit
14. if `delivery mode = occasional`, ask whether the send triggers or rate limit should be changed
15. ask which delivery path the user wants now and confirm that choice before writing route-specific setup
16. if Telegram is chosen, guide the user through the required Telegram configuration and record that `docs/telegram-send-flow.md` becomes the route-specific runtime reference
17. ask whether heartbeat push should be enabled
18. if heartbeat is enabled, explain that scheduled tasks are preferred and heartbeat-capable triggers are the fallback path
19. if heartbeat is enabled, ask which target location should receive the push
20. if heartbeat is enabled, ask whether the default heartbeat interval or target settings should be changed
21. ask whether agent mood should be enabled
22. if agent mood is enabled, ask whether mood should follow presets or conversation context
23. create or update `SOUL.md` so it retains the agent's personality markers, emotional baseline, and relationship tone that should guide emotional expression in context
24. create or update `AGENTS.md` so it is a required startup read, retains the current selfie send frequency such as `every_reply` or selected moments, and tells the agent to read `chat-selfie/send-flow.md` before any send
25. create or update `TOOLS.md` so it retains the concrete paths and invocation timing for mood, send-flow-related entries, seed helpers, send routes, and adapters
26. create or update `chat-selfie/send-flow.md` as the environment-specific runtime source of truth for future image sends, including current mood labels and when and why they should be used
27. ask whether the agent should stop after the current setup step or keep executing autonomously beyond it
28. persist the final setup summary into the target agent memory files
29. create or update references to `docs/self-upgrade.md` in the runtime memory files when persona evolution is part of the long-term setup
30. record the result into structured workspace artifacts
31. run the final review checklist and only mark the skill usable when every required file exists, is wired correctly, and the configured routes pass honest preflight checks
32. clearly mark which parts are ready now and which still require user action before selfie runtime can succeed

## Full-interaction rule

The whole startup flow should be completed through user interaction.

The agent should not skip ahead by silently choosing defaults just to make the workspace look initialized.

If the user has not yet answered a required startup question, the correct behavior is to keep guiding the conversation, not to fabricate a finished-looking setup.

When guiding the conversation, use the startup template as the default script shape instead of inventing a new structure from scratch.

## Repair rule

If the workspace already exists, do not discard it by default.

The agent must:
1. inspect current workspace files first
2. preserve user-owned files and local choices when possible
3. use `docs/self-repair.md` first when the problem is runtime diagnosis or auto-repair classification
4. repair only the missing, broken, or outdated parts
5. keep `chat-selfie/adapters/` intact unless the user explicitly asks to replace local adapter logic

If a route is missing or broken, say so directly and guide the user through the missing setup.

Repair should resume from the missing decision point, not restart as an autonomous roadmap unless the user explicitly requests a full rebuild.

## Portrait rule

Valid user-facing portrait setup paths:
1. the user provides a saved reference image
2. the user describes the appearance in natural language and the agent generates a base portrait

The second path is valid only when image generation is already available.

If generation is not ready, say so clearly and ask the user either to provide a reference image now or finish backend setup first.

## Tools and delivery explanation rule

Before asking the user to choose an implementation path, explain the practical difference between:
- repository-owned tool contracts
- workspace-owned local adapters
- cloud API generation
- local model generation
- another custom route the user already has

Before asking the user to choose a delivery route, explain the practical difference between:
- local framework delivery
- Telegram API delivery

Say clearly that local framework delivery is the default choice, but Telegram is usually the safer option when the current framework does not send images reliably.

Reuse an existing tested image route when possible.

## Occasional delivery rule

When `delivery mode = occasional`, explain that Chat Selfie does not send on every turn.

By default, explain:
- one initial send may happen for the `new` trigger
- later sends should be chosen from context, such as user-requested sends, large task completion, or emotional conversation moments
- the default rate limit is one image per agent every 15 minutes
- the limit can be customized by changing both the time window and the maximum image count inside that window

Tell the user about that limit even when they keep the default values, then ask whether they want to modify it.

The agent may recommend the default, but must not silently lock it in.

## Mood rule

Before asking whether mood should be enabled, explain it in plain language.

The user should understand that mood means:
- each generated image can reflect a more fitting emotion, expression, and state based on the current conversation context
- this helps the agent feel emotionally alive instead of sending images that all feel emotionally flat
- when mood is on, the same character can look shy, calm, playful, clingy, happy, tired, or otherwise appropriate to the moment

The agent should normally recommend turning mood on, because emotional variation is one of the core parts of Chat Selfie.

If mood is enabled, also explain the difference between:
- preset-driven mood: more stable, easier to control
- context-driven mood: more adaptive, more expressive, but sometimes less predictable

## Heartbeat rule

Before asking whether heartbeat should be enabled, explain it in plain language.

The user should understand that heartbeat means:
- the agent can proactively send a photo or short update even when the user did not just send a new message
- this is meant to create a feeling of ongoing presence
- it should usually be used more carefully than normal reply-time selfies

When heartbeat push is enabled, also explain:
- scheduled tasks are the preferred trigger mechanism
- another heartbeat-capable trigger may be used only when scheduled tasks are not practical
- heartbeat should resolve mood first, then generate an image, then send a short caption and image to the configured target

Ask where heartbeat pushes should go, and record that target in structured config.

## Persistent memory rule

At the end of initialization, persist the final setup so future conversations can recover the correct send behavior.

Required persistence destinations:
- `SOUL.md`
- `AGENTS.md`
- `TOOLS.md`
- `MEMORY.md`
- `chat-selfie/send-flow.md`

If long-term persona evolution is part of the setup strategy, also persist where `docs/self-upgrade.md` should be consulted before future durable persona or mood changes are written.

Treat:
- installed package `tools/` as repository-owned and updateable
- target workspace `chat-selfie/adapters/` as user-owned and local

## Minimum required outputs

A setup pass must create or update:
1. `chat-selfie/startup.answers.json`
2. `chat-selfie/startup.record.json`
3. `chat-selfie/chat-selfie.json`
4. `chat-selfie/integration.md`
5. `chat-selfie/send-flow.md`
6. `chat-selfie/status.md`
7. `SOUL.md`
8. `AGENTS.md`
9. `TOOLS.md`

But those files do not by themselves mean setup is complete.
They count as completion only when they reflect collected user decisions rather than guessed placeholder defaults, and when image generation is actually available or truthfully marked as still blocking readiness.

Those artifacts must retain:
- generation-method category
- selfie reference image path
- whether heartbeat is enabled
- whether agent mood is enabled
- selected delivery route
- delivery-mode runtime document
- whether the delivery route was explicitly chosen by the user
- route-specific runtime document
- whether the user was told Telegram is usually more stable
- whether fallback to local framework delivery is allowed
- occasional triggers, if occasional mode is active
- occasional rate-limit window and image count, if occasional mode is active
- whether the occasional rate limit was explained to the user
- heartbeat runtime document
- whether scheduled-task preference was explained
- selected heartbeat target
- whether heartbeat should use mood
- whether `chat-selfie/send-flow.md` was created or updated
- where `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and `SOUL.md` are expected to be updated
- whether `SOUL.md` now reflects the intended personality markers and emotional expression baseline
- whether `AGENTS.md` now records the current selfie frequency and the requirement to read `chat-selfie/send-flow.md` before sending
- whether `TOOLS.md` now records concrete mood, send-flow, send, and seed-related tool locations or truthfully records that one of those paths is still missing
- whether `chat-selfie/send-flow.md` now contains the current mood labels and the conditions and reasons for using them
- whether those memory files point runtime image-send work back to `chat-selfie/send-flow.md`
- whether runtime memory files also point durable persona evolution back to `docs/self-upgrade.md`
- whether Telegram configuration is ready when Telegram is chosen
- whether the user approved the Telegram route when Telegram is chosen
- whether setup stayed in guided mode or was explicitly authorized to continue autonomously

## Final review gate

Startup must not mark Chat Selfie as usable until a final review pass is complete.

That final review should happen after startup artifacts and runtime-facing memory files were created or updated.

The final review checklist must verify all of these:

1. `chat-selfie/chat-selfie.json` exists and is readable
2. `chat-selfie/startup.answers.json` exists and matches collected user decisions
3. `chat-selfie/startup.record.json` exists and truthfully reflects readiness
4. `chat-selfie/integration.md` exists
5. `chat-selfie/send-flow.md` exists and includes the environment-specific send flow, current mood labels, and the reasons and timing for using them
6. `chat-selfie/status.md` exists
7. `SOUL.md` exists and reflects the intended personality markers and emotional expression baseline
8. `AGENTS.md` exists, is treated as required startup reading, records the current selfie frequency, and tells the agent to read `chat-selfie/send-flow.md` before sending
9. `TOOLS.md` exists and records the concrete paths and call timing for mood, send, send-flow-related entries, seed helpers, and adapters that matter in this environment
10. the configured portrait path or portrait plan exists and is truthful
11. the configured mood route is readable or truthfully marked unavailable
12. the configured generation route passes honest preflight or is truthfully marked blocking readiness
13. the configured delivery route passes honest preflight or is truthfully marked blocking readiness
14. if heartbeat is enabled, the configured heartbeat target and trigger readiness are both truthfully recorded

This checklist is not limited to the headline files above.

It must cover every setup item that was decided during startup.

That means the final review must confirm that all configured content from the startup flow is now present, consistent, and truthfully retained, including:

- target agent identity
- persona direction or confirmed existing persona
- portrait source and saved path or truthful portrait plan
- generation-method category and backend readiness
- delivery frequency such as `every_reply` or selected moments
- occasional trigger policy and rate-limit settings when occasional mode is active
- delivery route and route-specific readiness
- heartbeat enablement, target, interval, and trigger readiness when heartbeat is enabled
- mood enablement, mood mode, and the current environment's mood labels and usage reasons when mood is enabled
- the required `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and `chat-selfie/send-flow.md` updates
- the structured workspace artifacts and runtime-facing memory references

If startup asked for it, confirmed it, configured it, or recorded it, the final review checklist must verify it before the skill can be marked usable.

The startup pass should also run a practical smoke-check review:

- confirm the configured files are readable from their recorded paths
- confirm required route references point to real files or real existing system capabilities
- confirm there is no file that claims a route is ready while the referenced route is missing
- confirm the workspace can honestly decide whether the next turn should send, skip, degrade, or repair

Only after that review succeeds may the skill be treated as usable for normal runtime.

If any checklist item fails, the correct result is not "usable with assumptions."

The correct result is:

- stay in setup
- enter repair
- or mark the workspace as not yet ready

Startup must not end with unresolved checklist items.

An unfinished checklist means startup is still incomplete, even if some files already exist.

## Ready vs incomplete state

Treat the workspace as minimally ready for normal runtime only when:
1. `chat-selfie/chat-selfie.json` is present and readable
2. `chat-selfie/startup.record.json` truthfully reflects what is ready and what is not
3. the required startup decisions have actually been collected from the user or explicitly confirmed by the user
4. a real image-generation path is available now
5. the selected delivery path is either usable now or truthfully marked as still pending
6. the portrait path or portrait plan is truthfully recorded
7. `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and `chat-selfie/send-flow.md` all exist and reflect the current setup
8. the final review checklist has completed successfully

If those conditions are not met, the workspace is incomplete and the agent should stay in setup or repair mode.