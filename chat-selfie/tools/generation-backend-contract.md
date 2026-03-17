# Generation Backend Contract

## Purpose

Define the minimum contract any image-generation route must satisfy.

## Input shape

A generation request should be able to carry:

- target agent identity
- portrait anchor or portrait reference
- current mood or state description
- visual scene intent
- optional style constraints
- optional backend-specific overrides

## Output shape

A generation result should return at least:

- success or failure
- image path, url, or binary reference
- optional revised prompt summary
- optional debug notes

## Categories

- existing system route
- hosted API route
- local model route
- other custom route
