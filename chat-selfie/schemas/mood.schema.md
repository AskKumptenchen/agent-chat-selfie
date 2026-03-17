# Mood Schema

## Two supported modes

### 1. Preset mode
The system uses named states with stable meanings.

Suggested fields:
- state key
- human label
- description
- tone hint
- visual hint

### 2. Context mode
The system generates a state description from recent context.

Suggested fields:
- context window size
- inference instruction
- optional guardrails
