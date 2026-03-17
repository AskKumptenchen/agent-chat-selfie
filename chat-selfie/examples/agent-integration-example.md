# Agent Integration Example

## Goal

Show how an agent would integrate Chat Selfie into its own persona stack.

## Example mapping

- `SOUL.md` defines the emotional baseline and relational tone.
- `IDENTITY.md` defines visual anchors and common expressions.
- `AGENTS.md` defines when Chat Selfie should be loaded and triggered.

## Example trigger policy

- send on every reply only when explicitly enabled by the user
- otherwise default to occasional sends on task completion and direct user request
- heartbeat sends must be negotiated separately

## Example guided setup behavior

- if the user says `help me configure Chat Selfie`, first clarify whether they want config only or config plus implementation
- explain backend and delivery choices in ordinary language before asking for a selection
- confirm major branch decisions before writing files
- if the user says `continue`, move to the next setup question by default instead of starting a new implementation phase
- summarize setup progress as confirmed decisions and pending choices, not only as internal milestones
