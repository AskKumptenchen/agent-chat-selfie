# Chat Selfie Workspace Layout

After installation, Chat Selfie should guide the target agent to create a local `chat-selfie/` directory inside the target workspace.

## Minimum initialization layout

```text
chat-selfie/
  README.md
  send-flow.md
  startup.answers.json
  startup.record.json
  chat-selfie.json
  integration.md
  status.md
```

## Runtime layout

```text
chat-selfie/
  heartbeat.py
  README.md
  send-flow.md
  startup.answers.json
  startup.record.json
  chat-selfie.json
  integration.md
  generate.py
  mood.py
  mood-pool.json
  mood-log.jsonl
  send.py
  send_telegram.py
  status.md
  portrait/
  selfies/
  adapters/
    README.md
```

## Optional layout

```text
chat-selfie/
  generation-plan.md
  occasional-limit-log.jsonl
  repair-log.jsonl
  portrait/
    agent_profile.png
  adapters/
    mood/
    generation/
    delivery/
```

## Config role

`chat-selfie/chat-selfie.json` is the workspace-wide config entry.

It should retain:

- target agent and workspace identity
- important local paths
- portrait, generation, and delivery settings
- selfies output path
- heartbeat settings
- heartbeat target settings
- persistence targets for AGENTS.md, TOOLS.md, MEMORY.md, and SOUL.md review
- mood settings and mood file paths
- repository-owned tool choices and workspace adapter choices
- self-repair policy and repair record paths

## Minimum runtime-ready state

The workspace should be treated as minimally ready for normal runtime only when it has truthful, readable state for:

- `chat-selfie/chat-selfie.json`
- `chat-selfie/startup.record.json`
- the selected generation and delivery path
- the current portrait path or portrait plan

The runtime helper scripts such as `mood.py`, `generate.py`, `send.py`, `send_telegram.py`, and `heartbeat.py` belong to the runnable workspace layout, but they do not all need to exist before initialization can truthfully record an incomplete or repair-needed setup state.

Other files may still exist for guidance, logs, or later expansion, but the agent should not claim runtime readiness if these minimum records are missing or misleading.

## Incomplete state

The workspace should be treated as incomplete when:

- one required state file is missing or unreadable
- the configured route no longer exists or no longer works
- the portrait path, generation path, or delivery path is recorded inaccurately
- the workspace still needs user action before selfie runtime can succeed

When this happens, the agent should re-enter repair-oriented setup instead of pretending the workspace is fully ready.

Runtime self-checks may also record repair attempts, degradation decisions, and remaining user actions in workspace-owned repair state before guided setup resumes.

## Ownership rule

- `chat-selfie/` is workspace-owned state created for one target agent.
- `chat-selfie/adapters/` is user-owned and may contain private adapter logic.
- repository-owned reusable tool contracts stay under the installed skill package `tools/`.
- repository-owned fixed logic such as `tools/mood_resolver.py` stays in the installed skill package.
- workspace-local `mood.py`, `mood-pool.json`, and `chat-selfie.json` should be copied or created during initialization and then customized locally.

## Update rule

When the Chat Selfie repository is updated:

- repository-owned docs and tool contracts may change
- local adapters under `chat-selfie/adapters/` should not be replaced by upstream updates
- the agent should migrate workspace files carefully instead of regenerating them blindly
