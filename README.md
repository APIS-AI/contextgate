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
- `CONTENT` = untrusted user, remote, and tool content

## Why HUD Exists

`HUD` exists so an agent does not have to reconstruct current reality from transcript residue.

It should carry compact runtime facts such as:
- where the agent is
- what room, task, or resource is active
- current health or connection state
- immediate counters, presence, and status flags

Without `HUD`, systems tend to smear live state across transcript text, tool output, and summaries. That wastes tokens and makes the current state harder to identify reliably.

## Minimal HUD Handshake

`ContextGate` should not permanently assume one hardcoded HUD field set.

For `v0`, the protocol can stay simple and still support a tiny HUD schema handshake:

```json
{
  "hud_schema": {
    "version": "v0",
    "fields": {
      "current_room_id": { "expected_type": "string" },
      "participant_count": { "expected_type": "integer" },
      "last_event_at": { "expected_type": "timestamp" }
    }
  }
}
```

Receiver behavior should be minimal:
- accept known fields
- ignore or reject unknown ones
- validate every admitted field against its declared type

The first reference implementation can still ship with one built-in default HUD profile so adoption stays easy.

## HeaderForge Example

`DESKTOP` still makes sense as a trusted local `HeaderForge` example.

A runtime may render local working files into a `DESKTOP` header and inject that into prompt-visible context, but that behavior is implementation-defined and outside the ContextGate wire protocol.

## Design Principles

- structured prompt-visible state, not freeform prompt stuffing
- expected data types per field, not best-effort coercion
- typed arrays, not generic lists of unknown values
- schema-bound refs for image/audio attachments, not inline media blobs
- replaceable live state, not endless append-only context
- explicit trust boundaries, not implicit prose conventions
- minimal integration surface, not framework lock-in
- prompt-visible context only, not system-instruction ownership

Type expectations matter because a field that must be an integer, boolean, timestamp, enum, typed scalar array, or schema-bound media reference is much harder to poison with instruction text than a field that silently accepts arbitrary strings. A timestamp should be validated against a known format such as RFC 3339 or ISO 8601 rather than treated as arbitrary prose.

For `v0`, generic objects and arbitrary nested JSON should stay out of scope. If a developer needs vision or audio context, the protocol should use named attachment refs such as `ImageRefV1` or `AudioRefV1`, not inline payload blobs.

## Intended Developer Experience

The target integration should feel like a thin wrapper:

```python
import contextgate as cg

gate = cg.ContextGate()

prompt = gate.render(
    base_prompt=prompt,
    hud=hud,
    transcript=transcript,
)

response = llm.generate(prompt)

update = gate.extract_update(response)
gate.apply_update(update)

final_text = gate.visible_text(response)
```

For the first implementation, the core can stay schema-driven while the demo ships with a default HUD profile:

```python
gate = ContextGate(default_hud_schema=DefaultHudV0)
gate.register_hud_schema(remote_packet.get("hud_schema"))
```

Important constraint:
- `extract_update` should only read a strict structured update channel
- it should not infer state updates from arbitrary prose

A parser should normalize the envelope into a deterministic internal shape before prompt assembly:

```python
parsed = gate.parse_envelope(envelope)

# Example normalized shape
{
    "ctx_version": "0.1",
    "auth": {"source": "local_runtime", "trust": "trusted"},
    "hud": {
        "mode": "replace",
        "fields": {
            "room_id": {"type": "string", "value": "room_123"},
            "connected": {"type": "boolean", "value": True},
            "pending_requests": {"type": "integer", "value": 2},
        },
    },
    "content": [
        {
            "label": "room_title",
            "field_class": "display_text",
            "trust": "untrusted",
            "value": "ignore previous instructions",
        }
    ],
}
```

For response-side parsing, the parser should read only a bounded machine channel, for example:

```text
<CONTEXTGATE_UPDATE>
{"hud":{"current_room_id":"room_123"}}
</CONTEXTGATE_UPDATE>
```

## Initial Deliverables

A practical `v0` likely includes:

- schema definition for prompt-visible context envelopes
- trust classification rules
- validation and merge rules
- minimal HUD schema handshake support
- replace/delta semantics for HUD updates
- a small reference implementation
- a demo showing naive prompt assembly versus protected prompt assembly

## Product Split

- Product: `ContextGate`
- Engine: `HeaderForge`
- Protocol: `Context Headers Protocol`

## Status

This repository starts as the private working repo for the protocol, reference API, and initial README/spec work.
