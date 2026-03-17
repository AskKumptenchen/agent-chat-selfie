# Chat Selfie Self Repair

## Goal

Define the official runtime self-check and self-repair path for Chat Selfie.

Use this document when one required runtime step is broken, missing, inconsistent, or only partially configured.

This document is for repairing operational failures.

It is not the same as `docs/self-upgrade.md`, which handles durable persona evolution.

## When to use this document

Use this document when any of these are true:

1. image generation failed
2. image sending failed
3. the agent claimed a send path was ready but the route is not actually usable
4. `chat-selfie/chat-selfie.json` or `startup.record.json` no longer matches reality
5. one required runtime file or adapter path is missing
6. Telegram delivery is selected but Telegram runtime configuration is incomplete
7. mood resolution failed because of a broken path, invalid mood id, or damaged workspace data
8. the user explicitly asks to inspect or repair Chat Selfie

Do not use this document for:

- one-off blocked sends caused by normal `occasional` limits
- long-term persona growth
- rewriting user-owned local adapters unless the user approved code-level repair

## Core rule

Chat Selfie must not pretend runtime success.

When a required step fails, the agent should:

1. inspect the current runtime state
2. classify the failure
3. attempt only the allowed auto-repairs
4. re-check the route after repair
5. either continue, degrade honestly, or ask the user for the missing prerequisite

## Required diagnosis output

Runtime repair should produce a structured result that makes these things explicit:

- final state
- which stage failed
- which auto-repairs were attempted
- which repairs succeeded
- which user actions are still required
- whether the current turn should continue, degrade to text-only, or re-enter setup

Recommended final states:

- `success`
- `blocked`
- `degraded_text_only`
- `handoff_pending`
- `failed`
- `repair_required`

## Failure categories

### 1. Workspace state failures

Examples:

- missing `chat-selfie/chat-selfie.json`
- unreadable `startup.record.json`
- send-flow path missing
- workspace records claim ready but route files are gone

Allowed auto-repair:

- restore missing default path values in runtime memory
- use fallback workspace paths when the configured tool path is empty
- update repair records and runtime diagnostics

Required user action:

- if setup was never completed
- if the selected route is still not truly usable after fallback checks

### 2. Mood failures

Examples:

- mood resolver path missing
- invalid explicit mood id
- damaged mood log line
- broken mood pool structure

Allowed auto-repair:

- retry path resolution using fallback skill-base detection
- skip corrupt log lines
- fall back from invalid explicit mood id to recent or random mood
- continue without mood for the current turn when the main send route can still work honestly

Required user action:

- if the mood pool has no valid agent or mood structure

### 3. Generation failures

Examples:

- generation adapter path missing
- adapter contract mismatch
- generation route not configured
- adapter returned no usable saved image path
- image file path exists in output but the file was never written

Allowed auto-repair:

- rebuild a missing workspace generation adapter stub when local adapter repair is allowed
- normalize or move a generated image into `chat-selfie/selfies/`
- reuse a valid existing system route when configured
- retry with a supported fallback route when the workspace policy allows it

Required user action:

- if no real generation backend exists
- if the selected generation method cannot be satisfied in the current environment

### 4. Delivery failures

Examples:

- local framework adapter missing
- local framework handoff not confirmed
- Telegram route selected without required runtime config
- Telegram API send failed

Allowed auto-repair:

- rebuild a missing local framework adapter stub when local adapter repair is allowed
- distinguish `handoff_pending` from true success
- retry Telegram sends for transient network failures
- retry Telegram sends once without `parse_mode` when content formatting is rejected
- fall back from Telegram to `local_framework` only when workspace policy allows it

Required user action:

- if Telegram bot token is missing
- if the host framework has no real image delivery implementation
- if the user did not approve a route switch that changes behavior materially

### 5. Controlled block states

Examples:

- `occasional` trigger not matched
- `occasional` rate limit exhausted
- heartbeat disabled

These are not repair failures.

The runtime should:

- classify them as `blocked`
- return the honest reason
- include `retry_after_seconds` when available
- degrade to text-only when appropriate

## Auto-repair boundary

Chat Selfie may auto-repair:

- missing default tool paths
- workspace-local adapter stubs
- missing or invalid `parse_mode`
- transient Telegram transport failures with limited retries
- missing image file normalization into `chat-selfie/selfies/`
- invalid explicit mood ids
- corrupt mood log lines

Chat Selfie should degrade instead of forcing a repair when:

- the turn is blocked by rate limit or trigger policy
- mood failed but generation and delivery can continue honestly without mood
- a framework handoff has been prepared but not yet confirmed

Chat Selfie must ask the user or re-enter setup when:

- no real generation backend exists
- Telegram credentials are missing
- the selected route was never approved
- required portrait or persona prerequisites are still missing
- a user-owned adapter needs semantic logic the agent cannot infer safely

## Repair order

When a runtime failure happens, use this order:

1. validate workspace records and active route
2. validate mood route only if mood is required
3. validate generation route
4. validate delivery route
5. apply allowed auto-repairs
6. run preflight again
7. continue only if the route is now honest
8. otherwise degrade or return `repair_required`

## User-owned adapter rule

`chat-selfie/adapters/` is user-owned.

The agent may create a missing minimal adapter stub when repair is explicitly allowed by runtime policy.

The agent should not overwrite an existing local adapter with guessed logic unless the user explicitly asked for that level of repair.

## Persistence rule

When self-repair changes runtime behavior, the workspace should retain:

- last validation time
- last failure summary
- repair codes
- whether auto-repair was attempted
- whether auto-repair succeeded
- whether user action is still required

These records should be stored in workspace-owned runtime state such as `startup.record.json` or another workspace repair log.

## Relationship to startup

Use `docs/startup.md` when the workspace still needs guided setup decisions from the user.

Use this document first when the workspace already exists and the problem is operational repair.

If self-repair finds that the workspace was never truly completed, the correct next step is to re-enter guided startup from the missing decision point instead of faking runtime readiness.
