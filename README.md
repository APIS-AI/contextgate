# ContextGate

ContextGate is a prompt-context boundary for agent systems.

It gives developers a small way to inject current structured state into prompts without treating transcript residue, tool output, and untrusted content as the same thing.

For the full protocol and design rationale, see [docs/TRUST_SCOPED_CONTEXT_HEADERS_PROTOCOL_PROPOSAL.md](docs/TRUST_SCOPED_CONTEXT_HEADERS_PROTOCOL_PROPOSAL.md).

## What It Does

- injects one current context envelope into each turn
- keeps live state replaceable instead of append-only
- separates trusted runtime state from untrusted content
- validates incoming fields against declared types or schemas
- supports a bounded machine update channel on response output
- fits into an existing prompt assembly pipeline

## Core Concepts

- `HUD`: replaceable live runtime state about what is true right now
- `CONTENT`: untrusted user, remote, or tool content
- `TRANSCRIPT`: optional historical residue
- `DESKTOP`: a trusted local `HeaderForge` example, not a `ContextGate` wire-protocol section

At steady state, only one active `ContextGate` envelope should be present in prompt-visible context. Older copies should be stripped before the next turn.

## Integration Shape

```python
import contextgate as cg

gate = cg.ContextGate(default_hud_schema=DefaultHudV0)
gate.register_hud_schema(remote_packet.get("hud_schema"))

prompt = gate.render(
    base_prompt=prompt,
    hud=gate.assemble_hud(remote_packet.get("hud")),
    content=remote_packet.get("content"),
    transcript=transcript,
)

response = llm.generate(prompt)

update = gate.extract_update(response)
gate.apply_update(update)

final_text = gate.visible_text(response)
```

Important constraint:
- `extract_update` should read only a strict structured update channel
- it should not infer state updates from arbitrary prose

## Update Channel

A minimal response-side machine channel can look like this:

```text
<CONTEXTGATE_UPDATE>
{"hud":{"current_room_id":"room_123"}}
</CONTEXTGATE_UPDATE>
```

## HUD Schema Handshake

`ContextGate` can accept a minimal declarative handshake for HUD fields:

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

Receiver behavior should stay simple:
- accept known fields
- ignore or reject unknown fields
- validate admitted fields against declared types

## Type Model

For `v0`, keep the field model small and explicit.

Allowed examples:
- `string`
- `integer`
- `boolean`
- `timestamp`
- `string[]`
- `integer[]`
- `timestamp[]`
- schema-bound refs such as `ImageRefV1` and `AudioRefV1`

Avoid in `v0`:
- arbitrary nested JSON
- generic `object`
- mixed-type arrays
- inline image or audio payloads

## HeaderForge

`HeaderForge` is the local header construction layer.

That is where a runtime can build trusted local headers such as `DESKTOP` from local files or runtime state before injecting them into prompt-visible context.

## v0 Goals

- define the prompt-visible context envelope shape
- support typed HUD validation and assembly
- support untrusted content classification
- support a bounded update channel
- provide a small reference implementation

## Non-Goals

- owning system instructions
- replacing an agent framework
- defining local working-file management
- storing full long-term memory inside the envelope

## Status

This repository is the private working repo for the protocol, reference API shape, and initial implementation work.
