# ContextGate Launch Brief

## Category

ContextGate is a context/state management layer for agent systems.

Public hook:

`A dynamic HUD-style context header for agents.`

Technical subtitle:

`A prompt-visible state layer that replaces live runtime state each turn instead of endlessly appending transcript residue.`

## One-Sentence Pitch

ContextGate gives an agent one structured, replaceable context envelope per turn so authoritative runtime state stays compact, untrusted content stays labeled, and state changes are parsed only from a strict machine update channel.

## What The Repo Already Proves

- A single prompt-visible envelope:
  - `contextgate/gate.py`
  - `contextgate/rendering.py`
- A strict machine update channel using tagged payload extraction:
  - `contextgate/update_channel.py`
- Clear separation between live state, untrusted content, and transcript residue:
  - `README.md`
  - `docs/CONTEXTGATE_PROTOCOL_PROPOSAL.md`
- A CLI that can render, extract, apply, diff, and validate updates:
  - `contextgate/cli.py`
- Runnable examples for wrapped provider outputs and shell loops:
  - `examples/cli_openai_chat_wrapper_pipeline.sh`
  - `examples/cli_anthropic_messages_wrapper_pipeline.sh`
  - `examples/cli_gemini_generate_content_pipeline.sh`
  - `examples/cli_combined_diagnostics.sh`

## Top 5 Failure Modes It Addresses

1. Transcript bloat
   - Long-running agents keep re-sending history, tool outputs, and stale state until prompts become expensive and noisy.
   - ContextGate keeps one active envelope and replaces live state instead of appending it.

2. State reconstruction from residue
   - Agents infer what is true now by re-reading old chat history.
   - ContextGate promotes current runtime state into HUD and treats transcript as optional residue.

3. Trusted and untrusted context collapse
   - Remote content, tool output, and local runtime state end up flattened into one prompt stream.
   - ContextGate separates authoritative state from untrusted content explicitly.

4. Accidental state updates from prose
   - Systems infer machine state changes from natural-language output.
   - ContextGate only accepts state changes from a strict update channel.

5. Weak operator visibility
   - Agent loops are hard to inspect because state changes are buried in chat text.
   - ContextGate exposes diffs, stderr channels, and update records through the CLI.

## Sharp Comparison Line

Transcript-heavy agents try to remember by re-sending history.

ContextGate tries to orient by re-sending one bounded, authoritative HUD.

## Likely Objections

### "Is this just JSON in the system prompt?"

No. The repo implements replacement semantics, strict update extraction, validation, and CLI/operator flows around the envelope rather than treating it as loose formatting.

### "Why not just keep state in the orchestrator?"

You still can. ContextGate is for the prompt-visible boundary between orchestrator state and model-visible state. It makes that boundary explicit and machine-readable.

### "Is this memory?"

Not in the long-term-memory sense. The core abstraction is live per-turn orientation, not archival recall.

### "Does this solve prompt injection?"

No. It reduces ambiguity and attack surface by separating authoritative state from untrusted content, but it is not a full security solution.

## Best First-Screen README Structure

1. Headline
   - `ContextGate is a dynamic HUD-style context header for agents.`
2. Subtitle
   - `It keeps live runtime state current without inflating prompt context, because the header is replaced each turn instead of endlessly appended.`
3. One-paragraph problem statement
   - transcript-heavy loops bloat prompts
   - stale history is a poor source of truth
   - trusted local state and untrusted remote data should not be mixed
4. Before/after snippet
   - transcript-heavy prompt assembly
   - single `<CONTEXTGATE_ENVELOPE>` block
5. Minimal quickstart
   - render envelope
   - extract update
   - apply update
   - strip visible text
6. Deep links
   - protocol proposal
   - CLI pipelines
   - provider wrapper examples

## Launch Readiness Checklist

- Root `LICENSE` file present
- README does not describe the project as a private repo
- First screen includes a before/after example
- One copy-paste quickstart works in under five minutes
- One short demo shows prompt growth before vs after ContextGate
- Launch copy avoids overclaiming security guarantees

## Recommended Audience

- agent infrastructure builders
- prompt assembly/runtime engineers
- tool-using agent developers
- platform/security engineers dealing with untrusted retrieved content

## Recommended Next Steps

1. Move a before/after prompt example higher in `README.md`.
2. Keep public copy focused on HUD, trust separation, and live replacement.
3. Launch with one concrete integration or agent loop, not only the library in isolation.
