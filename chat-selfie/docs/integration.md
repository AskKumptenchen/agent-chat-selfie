# Chat Selfie Integration

Chat Selfie should attach to the target agent's existing persona stack instead of replacing it.

It should also keep repository-owned tool contracts separate from workspace-owned adapters.

## Persona file mapping

- `SOUL.md` should define the agent's long-term personality markers, emotional baseline, relationship tone, and the allowed mood range that tells the agent how to express feeling in context.
- `IDENTITY.md` should define visual anchors, recurring appearance traits, and voice cues that help captions feel consistent.
- `AGENTS.md` should be required session-start reading, retain the current selfie frequency policy such as `every_reply` or selected moments, and explicitly tell the agent to read `chat-selfie/send-flow.md` whenever a send may happen.
- `TOOLS.md` should define the concrete paths and invocation timing for Chat Selfie tools such as mood, send-flow-related entries, seed helpers, send routes, and any adapters, and should still point runtime send behavior back to `chat-selfie/send-flow.md`.
- `MEMORY.md` should record that Chat Selfie is configured, which delivery frequency is active, and point runtime send behavior to `chat-selfie/send-flow.md`.
- `docs/self-upgrade.md` should define how durable persona growth changes `AGENTS.md`, `SOUL.md`, and workspace mood data over time.
- `docs/self-repair.md` should define how runtime route failures are diagnosed, auto-repaired, degraded, or sent back into guided setup.

## Integration summary

Chat Selfie integration is not limited to `SOUL.md`, `IDENTITY.md`, and `AGENTS.md`.

The complete persistent integration surface is:

- `SOUL.md`
- `IDENTITY.md`
- `AGENTS.md`
- `TOOLS.md`
- `MEMORY.md`
- `chat-selfie/send-flow.md`

## Persistent runtime file

`chat-selfie/send-flow.md` should be created inside the local `chat-selfie/` workspace.

It should remain the concrete runtime source of truth for:

- delivery order
- trigger policy
- mood-id usage
- the current mood labels for this environment
- when each mood label should be used and why
- tool-call order
- route-specific send rules

`AGENTS.md`, `TOOLS.md`, and `MEMORY.md` should all point back to this file before image generation happens.

When durable persona growth happens, runtime memory should also point to `docs/self-upgrade.md` before rewriting long-term mood or persona files.

When runtime delivery, generation, or mood routes fail, runtime memory should also retain that `docs/self-repair.md` is the first repair reference before setup is restarted.

## Recommended default policy

For a first install, the safest default is:

1. persona source from existing persona files
2. portrait source from a saved reference image
3. delivery mode set to occasional
4. heartbeat disabled until separately negotiated

## Tools and adapters ownership

- Repository-owned tool contracts live in the installed Chat Selfie package `tools/`.
- Workspace-owned adapters live in `chat-selfie/adapters/`.
- The agent should read repository tool contracts first, then decide whether an existing system route or a local adapter will satisfy them.
- Local adapters may reflect one user's custom personality, mood logic, or delivery behavior, so they should not be overwritten by repository updates.

## Existing image workflow reuse

If the target agent already has a working OpenClaw image path or another tested generation route, Chat Selfie should reuse it.

If no route exists yet, the setup should delay generated portraits and let the user start with a stable reference image.

When the user is configuring Chat Selfie, integration behavior should remain guided-first:
- clarify scope before broad changes
- confirm major branch choices
- summarize configuration state instead of defaulting to milestone-language progress reports
- treat `continue` as the next guided setup step unless the user explicitly authorizes autonomous execution

If setup changes the persona or emotional baseline, `SOUL.md` should be reviewed and updated so Chat Selfie behavior remains aligned with the agent's identity.

If long-term interaction changes the agent's personality or emotional habits, the workspace mood json should also be reviewed and updated so mood ids, prompts, and prompt parts stay aligned with the evolved persona.
