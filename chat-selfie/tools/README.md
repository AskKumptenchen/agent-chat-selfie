# Chat Selfie Tools

This directory contains repository-owned tool contracts shipped with the publishable Chat Selfie skill.

## Purpose

These files describe reusable capabilities that an agent may rely on while keeping user-specific adapter logic local to the target workspace.

## Ownership boundary

- `tools/` in the installed skill package is repository-owned and may be updated with new versions of Chat Selfie.
- `chat-selfie/adapters/` in the target workspace is user-owned and should remain local.

## Invocation rule

When the agent wants to use a tool from this directory, it should:

1. read the relevant tool contract
2. check whether the target workspace already has a matching local adapter
3. reuse an existing system route when available
4. otherwise guide the user to create or configure a local adapter
