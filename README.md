# ContextGate

ContextGate is a prompt-visible session context layer for agent systems.

It is designed to solve a narrow but increasingly important infrastructure problem: agent stacks routinely flatten trusted state, untrusted external content, tool output, and transcript residue into one prompt-visible blob. That wastes tokens and makes prompt injection easier.

ContextGate introduces a thin, drop-in boundary layer that developers can place in front of an existing prompt assembly pipeline.

At steady state, only one active ContextGate envelope should be present in prompt-visible context. Older copies are stripped before the next turn, so the protocol adds very little overhead compared with transcript-style repetition.

## What It Does

- injects a fresh structured context overlay on each turn
- keeps only one current context envelope in prompt-visible state
- separates prompt-visible state from transcript residue
- supports replace-not-append semantics for live HUD state
- classifies prompt-visible inputs by trust and role
- keeps untrusted content as content rather than silent authority
- fits into existing LLM pipelines without requiring a framework rewrite

## Scope

ContextGate starts below system instructions.

In scope:
- `HUD`: replaceable live operational state about what is true right now
- `DESKTOP`: editable working state the agent is actively using
- `CONTENT`: untrusted user, remote, and tool content
- `TRANSCRIPT`: optional historical residue

Out of scope:
- system prompts
- immutable operator control
- top-level instruction hierarchy
- runtime-specific control-plane composition

## Why This Exists

Current agent systems have three recurring failures:

1. Untrusted text can silently masquerade as authority.
2. Chat-history continuity is repetitive, lossy, and expensive.
3. Remote context exchange is unsafe by default when structure and trust are not explicit.

ContextGate treats prompt-visible continuity as a typed state transport problem instead of a transcript-reconstruction problem.

The intended steady-state cost is:
- one current envelope
- old envelopes removed
- compact snapshots or deltas when possible

Practical distinction:
- `HUD` = runtime facts and environment status
- `DESKTOP` = current notes, priorities, and working state

## Why HUD Exists

`HUD` exists so an agent does not have to reconstruct current reality from transcript residue.

It should carry compact runtime facts such as:
- where the agent is
- what room, task, or resource is active
- current health or connection state
- immediate counters, presence, and status flags

Without `HUD`, systems tend to smear live state across transcript text, tool output, and summaries. That wastes tokens and makes the current state harder to identify reliably.

## Why DESKTOP Exists

`DESKTOP` exists so an agent can keep a small editable working surface that is distinct from live environment state.

It should carry current working material such as:
- priorities
- temporary notes
- active decisions
- task-specific scratch context

Without `DESKTOP`, systems tend to mix scratch work with transcript history or tool content. That makes editing, replacing, and preserving current working context much harder.

The separation matters:
- `HUD` tells the agent what is true right now
- `DESKTOP` tells the agent what it is actively working with

## Design Principles

- structured prompt-visible state, not freeform prompt stuffing
- replaceable live state, not endless append-only context
- explicit trust boundaries, not implicit prose conventions
- minimal integration surface, not framework lock-in
- prompt-visible context only, not system-instruction ownership

## Intended Developer Experience

The target integration should feel like a thin wrapper:

```python
import contextgate as cg

gate = cg.ContextGate()

prompt = gate.render(
    base_prompt=prompt,
    hud=hud,
    desktop=desktop,
    transcript=transcript,
)

response = llm.generate(prompt)

update = gate.extract_update(response)
gate.apply_update(update)

final_text = gate.visible_text(response)
```

Important constraint:
- `extract_update` should only read a strict structured update channel
- it should not infer state updates from arbitrary prose

## Initial Deliverables

A practical `v0` likely includes:

- schema definition for prompt-visible context envelopes
- trust classification rules
- validation and merge rules
- replace/delta semantics for HUD updates
- a small reference implementation
- a demo showing naive prompt assembly versus protected prompt assembly

## Product Split

- Product: `ContextGate`
- Engine: `HeaderForge`
- Protocol: `Context Headers Protocol`

## Status

This repository starts as the private working repo for the protocol, reference API, and initial README/spec work.
