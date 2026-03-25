# Chat Selfie for ClawHub

Language docs:
- English: `../README.md`
- 简体中文: `../docs/README.zh-CN.md`
- 日本語: `../docs/README.ja.md`

<p align="center">
  <img src="../docs/cover.webp" alt="Chat Selfie Cover" width="100%" />
</p>

`chat-selfie` is the publishable ClawHub skill package for this repository. Its job is to teach an agent how to initialize and maintain a local `chat-selfie/` workspace, not to ship one fixed image-generation plugin.

## Install

After the skill is published to ClawHub, install it into an OpenClaw workspace:

```bash
clawhub install chat-selfie
```

By default, `clawhub` installs the skill under the current workspace `./skills` directory. OpenClaw will load it in the next session.

## What happens after install

The first responsibility of the skill is to guide the target agent to create a local `chat-selfie/` directory in the current workspace.

That local directory should hold:

- workspace state such as `startup.answers.json`, `startup.record.json`, `chat-selfie.json`, `send-flow.md`, and `status.md`
- the persisted portrait reference image under `chat-selfie/portrait/`
- user-provided mood asset images saved under `chat-selfie/stickers/` when fixed mood-asset mode is used
- generated images under `chat-selfie/selfies/`
- user-owned adapters under `chat-selfie/adapters/`

The workspace layout contract lives in `docs/workspace-layout.md`.

## First-run startup

When the agent sees this skill for the first time, it should:

1. confirm which agent is being configured
2. inspect whether stable persona files already exist
3. ask whether the portrait should come from a saved reference image or a text-generated base portrait
4. check whether the current agent already has a working image-generation route
5. ask whether reply-time and heartbeat sends should use real-time generation or a fixed mood-asset pack
6. create or update the local `chat-selfie/` directory
7. if fixed mood-asset mode is chosen, guide the user to send the mood images, save them under the local workspace, and record the saved `asset_path` values
8. if no working route exists and the user still wants real-time generation, explain backend or adapter setup before asking for provider choices
9. ask when selfies should appear in chat
10. explain delivery route choices, including the Telegram route when relevant
11. explain occasional limits or heartbeat settings when those modes are selected
12. create or update `SOUL.md`, `AGENTS.md`, `TOOLS.md`, and `chat-selfie/send-flow.md` so runtime behavior, tool locations, personality markers, and send rules are all aligned
13. persist the result into structured workspace artifacts and runtime memory files
14. run the final startup review and only treat the skill as usable when all required files exist and the configured routes pass honest preflight

The detailed startup contract lives in `docs/startup.md`.

## Best integration path

Chat Selfie works best when the target agent already has:

- `SOUL.md` for emotional baseline and relationship tone
- `IDENTITY.md` for visual and voice anchors
- `AGENTS.md` for runtime loading and trigger conventions
- `TOOLS.md` for tool-call conventions
- `MEMORY.md` for durable runtime reminders

If the agent already has an OpenClaw image workflow or another tested generation route, Chat Selfie should reuse it instead of forcing a new provider.

If no image generation route exists yet, the safest first setup is usually:

- use a saved reference image for the portrait anchor
- keep delivery mode on occasional sends
- delay text-generated portrait setup until generation capability is working

## Tools and adapters

Chat Selfie now separates repository-owned tools from user-owned adapters.

- `tools/` in the installed skill package contains repository-owned tool contracts that may be updated with the repository.
- `chat-selfie/adapters/` in the target workspace contains user-owned local adapters and should not be overwritten by upstream updates.

For example, the repository may define a mood tool contract, but the target agent can satisfy that contract with:

- an existing system route
- a local custom mood adapter
- another user-provided implementation

## Runtime modes

The current skill package supports these runtime patterns:

- `every_reply` for per-turn selfie generation
- `occasional` for context-triggered sends with configurable rate limiting
- `heartbeat` for proactive pushes triggered by scheduled tasks or another heartbeat-capable mechanism

Within those runtime patterns, the active image source may be either:

- real-time generation
- fixed mood-asset mode that reuses a workspace-local image previously saved from user-provided mood assets and mapped to the resolved mood

The corresponding runtime docs are:

- `docs/reply-time-selfie-flow.md`
- `docs/occasional-delivery.md`
- `docs/heartbeat-delivery.md`
- `docs/telegram-send-flow.md`
- `docs/self-upgrade.md`

## Reply-time selfie flow

For the `every_reply` route, the standard per-turn behavior is:

1. user sends a message
2. agent reasons and handles the message normally
3. before the final reply is emitted, the agent resolves mood when enabled
4. the agent either builds an image prompt from mood, persona, and context or selects the mapped local mood asset
5. the agent hands the resolved image path and reply context to the selected delivery route

The detailed flow, including async send, sync send, sync send using an existing image capability, and fixed mood-asset mode, is documented in `docs/reply-time-selfie-flow.md`.

## Runtime memory and send flow

The initialized workspace should treat `chat-selfie/send-flow.md` as the concrete runtime source of truth for:

- trigger policy
- mood usage
- tool-call order
- delivery order
- route-specific rules

The agent should also persist runtime reminders into `AGENTS.md`, `TOOLS.md`, and `MEMORY.md`, and review `SOUL.md` when persona or emotional baseline changes.

For durable persona growth and mood evolution, the skill package provides `docs/self-upgrade.md`.

## Included examples

This publishable package includes:

- `SKILL.md` for OpenClaw skill loading
- `docs/startup.md` for the agent-facing startup contract
- `docs/reply-time-selfie-flow.md` for per-turn selfie behavior in `every_reply` mode
- `docs/occasional-delivery.md` for occasional trigger and rate-limit behavior
- `docs/heartbeat-delivery.md` for proactive heartbeat pushes
- `docs/telegram-send-flow.md` for Telegram API delivery
- `docs/self-upgrade.md` for durable persona and mood evolution
- `docs/workspace-layout.md` for the local workspace directory contract
- `docs/integration.md` for persona-file integration guidance
- `tools/` for repository-owned tool contracts
- `examples/` for portable startup, persona, and agent-learning examples
- `schemas/` for portable data shapes
- `templates/` for reusable workspace and persona templates
- `presets/` for optional default mood and delivery presets

The `examples/` directory now includes both structured artifact examples and learning-oriented prose examples.

Those prose examples are meant to help an agent understand how to apply the rules in realistic situations. They are not the primary hard-contract source; the normative behavior still lives in `docs/`, `schemas/`, and `tools/`.

Current learning-oriented examples include:

- `examples/mood-resolution-example.md` for mood choice and prompt-part mapping
- `examples/heartbeat-example.md` for heartbeat explanation, confirmation, runtime flow, and honest fallback behavior
- `examples/self-upgrade-example.md` for durable persona change versus temporary emotion
- `examples/startup-conversation-example.md` for guided-first startup dialogue
- `examples/occasional-trigger-example.md` for occasional trigger judgment and rate-limit behavior
- `examples/soul-integration-example.md` for what belongs in `SOUL.md` and what does not
- `examples/agents-integration-example.md` for session routing and when runtime should enter `chat-selfie/send-flow.md`
- `examples/tools-integration-example.md` for tool-call conventions, paths, and the boundary with runtime rules
- `examples/send-flow-runtime-example.md` for a complete runtime `chat-selfie/send-flow.md` example

## Local publish command

From the repository root, the intended first publish flow is:

```bash
clawhub publish ./chat-selfie --slug chat-selfie --name "Chat Selfie" --version 0.1.0 --tags latest
```

## Release scope

The current ClawHub package is documentation- and template-driven:

- startup guidance
- workspace initialization guidance
- tool-contract guidance
- persona and delivery integration guidance
- runtime mode docs for reply-time, occasional, heartbeat, and Telegram delivery
- runtime support for both real-time generation and fixed mood-asset delivery
- workspace templates for mood, generation, send, Telegram send, heartbeat, and send-flow
- portable example artifacts

It does not yet promise one fixed image provider, one fixed local stack, one production send binding, or one fixed adapter implementation.
