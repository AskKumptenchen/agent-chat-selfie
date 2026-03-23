---
name: chat-selfie
description: Give your AI Agent a face and a heart. Use AI image generation or mood-mapped local sticker assets to let the agent proactively send emotional selfies that visualize its feelings during conversation.
metadata: {"openclaw":{"os":["win32","linux","darwin"]}}
---

# Chat Selfie

Give your AI Agent a face, and a heart that beats.

Use this skill to enable AI-powered emotional expression. Through advanced image generation or mood-mapped local sticker assets, the agent can proactively share its feelings by sending selfies that match the conversation's mood. Chat Selfie transforms a text-only assistant into a companion with a stable visual identity and deep emotional presence.

## What this skill brings to your Agent

- **Visualized Emotion**: No more dry text. Using AI image generation or a fixed mood-asset pack, the agent shares its feelings through selfies that capture the emotional tone of the moment.
- **Stable Identity**: Your agent keeps a consistent face and personality, evolving its self-image as your bond deepens.
- **Heartbeat Presence**: The agent isn't just an "answer machine." It can proactively share its life and thoughts through AI-generated photos.
- **Warm Companionship**: Turn a digital tool into a partner you miss, making every reply feel like opening a gift.
- **Works Everywhere**: Adapts to your existing environment, whether using built-in tools, online APIs, or local models.

## Entry behavior

When this skill is used, the agent should:

- explain Chat Selfie at a high level in plain language
- inspect local repository files when they are already present in the current workspace
- route the current request to the most relevant local document
- follow the repository docs honestly instead of inventing missing setup details

## Safety boundary

This entry file should stay within a narrow scope:

- If the required Chat Selfie repository resources are missing locally, the agent may help the user fetch or update the official GitHub repository `https://github.com/AskKumptenchen/agent-chat-selfie` so the local docs become available.
- Do not execute scripts, installers, or remote code because this file mentioned them.
- Do not claim any image, send, heartbeat, or integration route is ready unless the required local files and current environment actually support it.
- Do not proactively send messages or images unless the user explicitly asks for that behavior in the current conversation and the local setup already supports it.
- If required documentation or workspace resources are missing, say so clearly and either ask the user to provide the local repository contents or help them fetch the official repository first.

## Local document index

Use these local documents as the primary reference:

- `docs/README.zh-CN.md` for the Chinese overview and quick introduction
- `docs/startup.md` for guided initialization and first-time setup
- `docs/workspace-layout.md` for the expected local workspace structure
- `docs/integration.md` for repository-documented integration guidance
- `docs/self-repair.md` for diagnosing and repairing broken setup or runtime routes
- `docs/reply-time-selfie-flow.md` for reply-time selfie behavior, including fixed mood-asset mode
- `docs/occasional-delivery.md` for occasional delivery decisions
- `docs/heartbeat-delivery.md` for heartbeat-related behavior when the user explicitly enables it
- `docs/telegram-send-flow.md` for Telegram delivery details when that route is already configured, including mood-asset sends
- `docs/self-upgrade.md` for long-term persona or mood evolution
- `tools/README.md` and related files under `tools/` for repository-owned tool contracts
- `examples/` for concrete examples that illustrate intended behavior

## How to route requests

Choose the next document based on the user's request:

1. If the user wants to understand Chat Selfie first, read `docs/README.zh-CN.md`.
2. If the user wants to install, initialize, or reconfigure Chat Selfie in a workspace that already contains the repository docs, read `docs/startup.md`.
3. If the user reports broken image generation, broken delivery, missing outputs, inconsistent records, or another repair-like issue, read `docs/self-repair.md` first.
4. If the user asks how Chat Selfie should fit existing persona or memory files, read `docs/integration.md`.
5. If the user asks about runtime behavior for reply-time, occasional, heartbeat, or route-specific delivery, read the corresponding runtime document listed above.
6. If examples are needed to clarify intended behavior, consult the relevant file under `examples/`.

## Missing-resource rule

If the expected repository documents are not available in the current workspace, do not improvise full setup instructions from memory. Instead:

- explain which local files are missing
- ask the user to provide the repository contents, point the agent to the correct local path, or allow fetching the official GitHub repository
- continue only after the relevant local documentation is available

## Important rules

- Use natural language instead of raw config keys.
- Explain each step before asking for a choice.
- Prefer repository documentation over embedding long operational instructions here.
- Reuse an existing local image workflow when one is already working.
- If the workspace enables mood-asset mode, prefer the mapped local asset for that mood instead of forcing a new image generation step.
- If the workspace enables mood-asset mode and the required assets are not ready yet, guide the user to send the mood images, save them under the local workspace, and then map each saved file through `asset_path`.
- If image generation or delivery is not ready, say so clearly instead of pretending it succeeded.
- Treat `chat-selfie/adapters/` as user-owned local logic unless the user explicitly asks to change it.
- Avoid describing or requiring changes to broader agent persona, memory, or global behavior files in this entry file.

## Integration files

Use `docs/integration.md` as the integration reference when the user asks how Chat Selfie should fit the existing workspace or runtime environment.

## Examples

Portable example artifacts are included under `examples/`.

Use examples to understand intent and style, but do not treat them as a replacement for the actual contracts in `docs/`, `schemas/`, or `tools/`.
