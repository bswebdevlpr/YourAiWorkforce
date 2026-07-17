# Hard problems solved

The engineering spine of this project: the non-obvious problems that came up taming a
stochastic 8B local model into a deterministic-enough pipeline, and how each was closed
(or deliberately left open). Each item is backed by code and traces. Some have deeper
write-ups in the blog series,
[**LangGraph Multi-Agent series**](https://bswebdev.hashnode.dev/series/lang-graph).

For the project overview and how to run it, see the [README](../README.md).

---

## 1. State isolation — two directions, one solved
A subagent's state can leak two ways, and only one is worth fully closing. **Outbound** — the
subagent's internal turns piling up in the parent thread — is solved: subagents run on a separate
`SubagentState`, and a `finalize` step uses `RemoveMessage` to strip those internal turns, leaving
the parent only a short summary. **Inbound** — the subagent's LLM still receiving the parent's
messages — is left in on purpose, compensated by a structured briefing packet; closing it fully
would have meant giving up LangGraph's native interrupt propagation (I tried, and resume broke).
The original "planner introduces itself as the PM" symptom was fixed separately — model swap +
persona hardening — not by isolation.
→ [src/subagents/state.py](../src/subagents/state.py) · [libs/subgraph.py:201](../src/libs/subgraph.py#L201)

## 2. Subgraph resume restarted from scratch every time
The checkpointer wasn't passed down to the subgraph, so the user's reply vanished from `messages`
and the conversation reset to turn 1. I injected the checkpointer consistently down to the subgraph
and made FastAPI (async) and `langgraph dev` **share the same sqlite file**.
→ [src/agent.py:170](../src/agent.py#L170)

## 3. `langgraph dev`'s sync-I/O block (blockbuster)
The dev middleware blocks synchronous I/O inside handlers, so the SqliteSaver connection failed.
I worked around it by opening the sqlite connection at **module load time** rather than inside
`graph()`, keeping it off the event loop. → [src/agent.py:150](../src/agent.py#L150)

## 4. A stochastic 8B, made deterministic — then measured
The `check_done` node asks a critic a single YES/NO question (*did the user just make another
request?*). Two problems, closed in order:

- **Determinism.** When the divergent planner (temp=0.5) made the call, it misjudged. I split off a
  **separate temp=0 critic instance** — the same `qwen3:8b` file, not a second model (`deepseek-r1:8b`
  was evaluated for this role and rejected: as a reasoning model it ignores the binary instruction
  and answers conversationally).
- **Efficiency, backed by numbers.** I instrumented every model call and found the critic was
  burning ~465 discarded thinking tokens (~25s) per YES/NO. Turning reasoning **off** collapsed that,
  but a labeled eval showed it also lost the ambiguous cases. The real fix was task design, not
  inference compute: a prompt biased toward *continue* on ambiguity (the safe direction for HITL).
  Result — **parity with thinking mode on the dominant case distribution at ~48× lower latency**.

→ [product_discovery/__init__.py](../src/subagents/planners/product_discovery/__init__.py) ·
**[harness + eval, reproducible](metrics/)**

## 5. Save-validation gate & response post-processing
- `_validate_prd`: checks required sections exist and no placeholders remain, **blocking incomplete
  artifacts from being saved**. → [product_discovery/tools.py:34](../src/subagents/planners/product_discovery/tools.py#L34)
- Response post-processing: strips `<think>` blocks, `🛑 [턴 종료]` markers, empty code fences, and
  greeting prefixes after turn 2, all via regex. → [src/libs/subgraph.py](../src/libs/subgraph.py)
- `_sanitize_query`: normalizes the orchestrator's hallucinated honorifics (e.g. "대표님!") into a
  noun phrase. → [src/agent.py:17](../src/agent.py#L17)

## 6. Hiding the save tool (dynamic tool binding)
Since the model ignored "don't save on turn 1", I made the **save tool conditionally bound** so it's
physically impossible to call. → [libs/subgraph.py](../src/libs/subgraph.py) (`model_with_save`)

## 7. Model-selection log
A decision record of how `gemma4:e4b` (4B) failed at following Korean negative-instruction lists —
with LangSmith trace evidence — and the move to `qwen3:8b`. → [docs/plan/model-use.md](plan/model-use.md)

## 8. The Python stream never says *why* it ended
The FastAPI endpoint streams raw model tokens and then simply closes. A turn that reached `END` and
a graph that **paused at an `interrupt()` waiting for human approval** are *byte-identical* on the
wire — both are "tokens, then EOF". A chat client can't tell whether to re-open the input box or to
render an approval prompt, and that distinction is the entire point of a HITL system.

The information exists — LangGraph's `snapshot.next` is non-empty exactly when the graph is paused —
it just never reaches the client. So the gateway **reconstructs it**: it relays the token stream,
and the moment the stream hits EOF it makes a *second* call (`GET /state/{thread_id}`) to ask why,
then emits an explicit `event: interrupt` or `event: done`.

That's the load-bearing reason the gateway exists, and it fixes the service split in place:
**Python owns the graph (tokens + state); Go owns the wire protocol the client actually consumes.**
The browser's event handling collapses to a four-case `switch` with nothing left to infer.
→ [gateway/main.go](../gateway/main.go) (`realUpstream`, `fetchState`) · [src/main.py](../src/main.py) (`GET /state/{thread_id}`)
