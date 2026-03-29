# ContextGate Launch Copy

## GitHub Repo Description

Dynamic HUD-style context headers for agents: trusted local state, untrusted remote data, and live replacement each turn without transcript bloat.

## Short Taglines

- Dynamic HUD-style context for long-running agents.
- Keep agent state in a HUD, not buried in chat history.
- Structured live context for agents, replaced each turn instead of endlessly appended.

## GitHub Release Draft

### Title

`v0.1.0: ContextGate initial public release`

### Summary

ContextGate is a dynamic HUD-style context header for agents. It keeps authoritative runtime state compact and current by replacing live state each turn instead of endlessly appending it through transcript history.

This release includes:

- a reference `ContextGate` implementation
- strict `<CONTEXTGATE_ENVELOPE>` rendering
- strict `<CONTEXTGATE_UPDATE>` extraction and validation
- CLI support for render/extract/apply flows
- diff, size, and stderr diagnostics for shell loops
- provider-wrapper examples for OpenAI-style, Anthropic-style, and Gemini-style outputs

### Why it exists

- transcript history is a poor source of truth for current state
- remote content should not silently become trusted authority
- agent loops need a compact, prompt-visible state layer
- operators need a strict machine update channel instead of prose parsing

### Good first example

Use the README quickstart and the provider wrapper examples in `examples/`.

## X Thread

1. ContextGate is a dynamic HUD-style context header for agents.

2. Most agent loops keep re-sending transcripts, tool outputs, and stale notes until the prompt becomes a mixed blob of state, residue, and untrusted text.

3. ContextGate takes a different approach:
   - one prompt-visible envelope per turn
   - authoritative HUD state kept separate from untrusted content
   - optional transcript residue
   - strict machine update channel

4. Instead of trying to remember by replaying more history, the agent re-orients from one bounded current-state header.

5. The repo includes:
   - Python library
   - CLI
   - update extraction/apply flows
   - stderr diagnostics
   - OpenAI / Anthropic / Gemini wrapper examples

6. Public hook:
   `Dynamic HUD-style context for long-running agents.`

7. Technical point:
   live state is replaced each turn instead of endlessly appended through transcript history.

8. If you build tool-using or long-running agents, this is the boundary layer between orchestrator state and prompt-visible state.

9. Repo: `https://github.com/APIS-AI/contextgate`

## Hacker News

### Title options

- Show HN: ContextGate, a dynamic HUD-style context header for agents
- Show HN: ContextGate, replaceable live context for long-running agents
- Show HN: ContextGate, prompt-visible state for agents without transcript bloat

### Post body

I built ContextGate to make prompt-visible agent state explicit and replaceable instead of reconstructing it from transcript history.

The core model is:

- HUD: authoritative runtime state
- CONTENT: untrusted remote/user/tool content
- TRANSCRIPT: optional residue

The repo includes a Python library, CLI, strict update extraction, stderr diagnostics, and runnable examples for OpenAI-style, Anthropic-style, and Gemini-style wrapped outputs.

The main claim is not “memory.” It is that long-running agents need a bounded current-state header that gets replaced each turn instead of endlessly appended.

I’d especially value feedback from people building agent runtimes, prompt assembly layers, and tool-using systems.

## Reddit

### r/LLMDevs

Built a small library called ContextGate for prompt-visible agent state.

The idea is simple:

- keep one current HUD/state header in the prompt
- keep untrusted remote content separate from authoritative state
- parse state changes only from a strict machine channel
- replace live state each turn instead of endlessly appending transcript residue

The repo includes a Python library, CLI, and runnable wrapper examples for OpenAI, Anthropic, and Gemini-style responses.

Main thing I want feedback on: is “dynamic HUD-style context header” a clear way to explain this, or is there a better public framing for the same idea?

Repo: `https://github.com/APIS-AI/contextgate`

### r/LocalLLaMA

Open-sourced a small agent-context library called ContextGate.

It’s aimed at long-running/tool-using loops where current state gets buried in transcripts and tool output.

Instead of replaying more history, it renders one prompt-visible envelope with:

- trusted HUD state
- untrusted content
- optional transcript residue

It also extracts state updates from a strict tagged channel, so the runtime doesn’t need to infer updates from prose.

If you’ve built agent loops and hit prompt bloat or “stale state in chat history” problems, this is the specific problem it is targeting.

Repo: `https://github.com/APIS-AI/contextgate`

## Suggested Next Assets

1. 30-second terminal demo showing prompt growth before vs after ContextGate.
2. One screenshot or gif of the CLI update/diff flow.
3. A concrete integration example outside the library itself.
