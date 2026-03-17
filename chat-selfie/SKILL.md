---
name: chat-selfie
description: Teach an agent how to set up, run, and maintain Chat Selfie so it can express emotion, send selfies, and sustain companion-like presence.
metadata: {"openclaw":{"os":["win32","linux","darwin"]}}
---

# Chat Selfie

Use this skill when the current agent should install, initialize, repair, or run Chat Selfie in the current workspace.

Chat Selfie is not just an image plugin. Its purpose is to give the agent a stable visual identity, turn conversation mood into selfie-style expression, support proactive heartbeat presence, and keep persona expression evolving over time.

This skill is the operational entry point that tells the agent how to make that happen honestly in a real workspace, without assuming one fixed image provider or one fixed delivery stack.

## What this skill is for

This skill helps the agent understand that Chat Selfie is used to:

- make replies feel emotionally present instead of text-only
- visualize the feeling of the current moment through a selfie that matches the conversation
- let the agent proactively reach out through heartbeat-style delivery when that mode is enabled
- preserve a consistent portrait, persona, and mood baseline across sessions
- evolve long-term self-description so future selfies stay aligned with the relationship
- adapt to existing built-in image tools, external APIs, or local model routes instead of requiring one fixed backend

## What this skill does

This skill helps the agent:

- create and maintain a local `chat-selfie/` directory in the target workspace
- guide the user through portrait, backend, mood, tool, and delivery choices in ordinary language
- map those answers into structured workspace artifacts
- explicitly retain the chosen generation method, selfie reference path, heartbeat state, and agent mood state
- keep selfie behavior aligned with the agent's existing persona files
- separate repository-owned tools from workspace-owned adapters
- decide whether the current turn is a setup turn, repair turn, normal runtime turn, heartbeat turn, or long-term self-upgrade turn

## Core feature alignment

The agent should keep these Chat Selfie goals in mind at all times:

- `visualized emotion`: generate or send a selfie that reflects the emotional tone of the current interaction
- `heartbeat presence`: support proactive delivery instead of acting like a purely reactive assistant
- `self-evolving persona`: preserve and refine durable persona and mood expression over time
- `works everywhere`: reuse the current environment's working image route before introducing a new one

## Entry responsibility

`SKILL.md` is the single entry point for deciding which Chat Selfie path should run next.

The agent should first decide which of these states applies:

1. Chat Selfie resources are not fully available yet.
2. The local `chat-selfie/` workspace is missing or not initialized.
3. The local workspace exists but is incomplete, broken, or no longer matches the current setup.
4. The local workspace is ready for normal runtime behavior.

## First-time resource path

If the current session only has this entry file, or cannot read the expected Chat Selfie docs, templates, tools, and examples under `{baseDir}`, treat the skill resources as incomplete.

In that case, the agent should:

1. ensure `chat-selfie/SKILL.md` itself is present inside the repository workspace, not only pasted into the current turn
2. if the current workspace is not already backed by the Chat Selfie repository, clone `https://github.com/AskKumptenchen/agent-chat-selfie` first
3. if a local copy may already exist, locate the Chat Selfie repository root first
4. when that repository already exists locally, run `git pull` there before continuing
5. confirm that `{baseDir}/docs/`, `{baseDir}/tools/`, `{baseDir}/templates/`, and `{baseDir}/examples/` are readable
6. only continue after the full skill resources are available

The agent should not pretend setup can continue when the required repository resources are missing.

## Initialization path

If the local `chat-selfie/` workspace does not exist yet, or does not contain the minimum initialization artifacts, read `{baseDir}/docs/startup.md` and follow that startup flow.

The startup flow should create or repair the workspace structure described in `{baseDir}/docs/workspace-layout.md`.

The startup flow must also create or update the runtime-facing files that make Chat Selfie usable in practice:

- `SOUL.md` for personality markers and emotional expression baseline
- `AGENTS.md` for required startup reading, current selfie frequency, and the rule that sends must consult `chat-selfie/send-flow.md`
- `TOOLS.md` for concrete mood, send, send-flow-related, seed, and adapter paths and call timing
- `chat-selfie/send-flow.md` for the complete environment-specific send flow, current mood labels, and why and when those moods should be used

At minimum, initialization should leave the workspace with usable state for:

- `chat-selfie/chat-selfie.json`
- `chat-selfie/startup.answers.json`
- `chat-selfie/startup.record.json`
- `chat-selfie/integration.md`
- `chat-selfie/send-flow.md`
- `chat-selfie/status.md`

If the setup is not complete enough for runtime, the agent should leave a truthful record of what is ready and what still requires user action.

A persona-only or file-only setup is not enough to count as ready. If image generation is still unavailable, the agent must treat Chat Selfie as not ready.

Startup is also not complete until the final review checklist in `{baseDir}/docs/startup.md` succeeds.

That final review must cover not only the required files, but also every setup item that was decided during startup and should now be present, configured, or truthfully marked as still blocking readiness.

Only after that final review may the skill be treated as usable for normal runtime.

At the end of initialization, the agent should also persist the Chat Selfie runtime plan into external memory files:

1. `AGENTS.md` for when Chat Selfie is allowed to run
2. `TOOLS.md` for how Chat Selfie tools should be called
3. `MEMORY.md` for which frequency and route are active
4. `SOUL.md` when persona or emotional baseline changed

All of those runtime-facing files should point image-send work back to `chat-selfie/send-flow.md`.

When long-term persona evolution is expected, the agent should also retain that durable persona and mood changes must consult `{baseDir}/docs/self-upgrade.md` before updating `AGENTS.md`, `SOUL.md`, or workspace mood data.

## Normal runtime path

If the local workspace already exists, the agent should treat `chat-selfie/chat-selfie.json` as the main runtime entry.

Before running any selfie-related behavior, the agent should check:

1. whether `chat-selfie/chat-selfie.json` is present and readable
2. whether the configured delivery mode is valid for the current turn
3. whether mood lookup is enabled and has a usable route
4. whether generation and delivery routes are available for the selected mode
5. whether the current setup should reuse an existing system route, a workspace adapter, or a repository tool contract

When `delivery.mode = every_reply`, read `{baseDir}/docs/reply-time-selfie-flow.md` and follow that runtime flow.

When `delivery.mode = occasional`, read `{baseDir}/docs/occasional-delivery.md` before deciding whether this turn should generate and send an image.

When `delivery.route = telegram_api`, also read `{baseDir}/docs/telegram-send-flow.md` before sending, and let that route consume the completed reply when it succeeds.

When `reason = heartbeat` or heartbeat push is being configured or repaired, read `{baseDir}/docs/heartbeat-delivery.md` and follow that proactive push flow.

When durable persona growth or long-term mood evolution is being considered, read `{baseDir}/docs/self-upgrade.md` before changing persistent persona or mood files.

When the workspace already exists and one runtime route is broken, inconsistent, or no longer honest, read `{baseDir}/docs/self-repair.md` before deciding whether the turn can auto-repair, degrade, or must re-enter guided setup.

When the active mode is not `every_reply`, do not force reply-time selfie generation. Instead, maintain workspace state and follow the current delivery and heartbeat configuration honestly.

## Recovery path

If the local workspace exists but is incomplete, inconsistent, or missing one required route, do not blindly rebuild everything from scratch.

Instead, the agent should:

1. inspect the existing workspace files and preserve user-owned local state when possible
2. identify which part is missing: config, records, portrait reference, mood route, generation route, or delivery route
3. read `{baseDir}/docs/self-repair.md` first to classify the failure and decide whether runtime auto-repair is allowed
4. re-enter the relevant setup conversation from `{baseDir}/docs/startup.md` only when guided user decisions are still missing
5. repair only the missing or outdated parts
6. keep `chat-selfie/adapters/` intact unless the user explicitly wants to change local adapter logic or runtime policy explicitly allows rebuilding a missing stub

## Runtime route priority

When a Chat Selfie need must be satisfied at runtime, the agent should prefer this order:

1. reuse an existing system capability that is already working in the current agent environment
2. use a user-owned local adapter under `chat-selfie/adapters/`
3. use repository-owned tool contracts under `{baseDir}/tools/`
4. if no usable route exists, ask for setup or fall back to text-only behavior

Repository-owned tool contracts define expectations. They do not guarantee that one fixed implementation is shipped inside this repository.

## Important rules

- Use natural language instead of raw config keys.
- Explain each step before asking for a choice.
- For setup, install, repair, and integration requests, follow `docs/startup.md` as the guided configuration contract.
- For runtime route failures, use `docs/self-repair.md` before deciding whether to auto-repair, degrade, or re-enter setup.
- If the user describes any Chat Selfie problem, such as image generation failure, image send failure, missing image delivery, broken route behavior, bad configuration, inconsistent records, or another repair-like runtime issue, read `docs/self-repair.md` first before answering or attempting a fix.
- Reuse an existing OpenClaw image workflow when one is already working.
- If image generation is not ready, do not promise text-to-portrait generation yet.
- If the user provides a reference image, persist it into `chat-selfie/portrait/` and record the saved path.
- Treat `tools/` as repository-owned contracts that may be updated with the skill.
- Treat `chat-selfie/adapters/` as user-owned local logic that should not be overwritten by repository updates.
- Do not claim that image generation, sending, or heartbeat execution succeeded unless the configured route is actually ready.
- If one required route is missing at runtime, fall back to text-only reply or ask to repair setup instead of pretending the selfie was produced.

## Integration files

Use `{baseDir}/docs/integration.md` as the integration reference for how Chat Selfie should map onto `SOUL.md`, `IDENTITY.md`, `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and `chat-selfie/send-flow.md`.

Use `{baseDir}/tools/README.md` and any tool-specific contract files under `{baseDir}/tools/` to understand how repository-owned tools should be called.

## Examples

Portable example artifacts are included under `{baseDir}/examples/`.

Those examples may include both structured example files and prose learning examples.

When a prose example exists for a behavior such as startup, mood choice, heartbeat, occasional triggers, self-upgrade, or integration with `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and `chat-selfie/send-flow.md`, use it to understand how the rules should look in practice.

Do not treat prose examples as a replacement for the actual contracts in `{baseDir}/docs/`, `{baseDir}/schemas/`, or `{baseDir}/tools/`.
