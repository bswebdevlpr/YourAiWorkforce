# YourAiWorkforce — Local 8B LLM Multi-Agent Orchestration

> **In one line**: a multi-agent planning pipeline that tames a *stochastic* 8B local
> model into behaving *deterministically enough to trust* — running entirely on a 16GB
> MacBook at **zero API cost**. A founder's rough idea → structured artifacts (PRD + architecture doc).

One orchestrator routes work to specialist subagents. A human approves each step. Every model call
runs on a local [Ollama](https://ollama.com) model (`qwen3:8b`, `deepseek-r1:8b`) — no API, no cost,
nothing leaves the machine.

It's built on [LangGraph](https://langchain-ai.github.io/langgraph/) `StateGraph`, and the whole
design follows one rule I kept relearning the hard way: **prompt is suggestion, graph is law.**

---

## Why this project

With a commercial API (GPT-4, Claude), multi-agent systems "just work" — but that's the
*model* doing the heavy lifting, and there's no engineering story in it. This project starts
from the opposite constraint:

- **An 8B local model breaks instructions probabilistically.** Tell the persona "don't call
  yourself the PM" and it does; tell it "don't call the save tool on turn 1" and it does;
  it leaks thinking tokens into its replies.
- **So instead of *trusting* the model, I *clamp* it.** A separate critic model, a save-validation
  gate, response post-processing, state isolation — wrapping each probabilistic component in a
  deterministic shell is the core of this repo.

> 📌 **Current scope**: **Phase 0** (idea → PRD → architecture) works end-to-end.
> [`agents/`](agents/) contains persona designs through Phase 1–6 (build / QA / deploy), but
> **only Phase 0 is wired in code** — the rest is roadmap ([see below](#implementation-status-vs-roadmap)).

---

## Architecture

```mermaid
flowchart TD
    START([START]) --> ORC[orchestrator<br/>qwen3:8b]
    ORC -->|tool_call| ROUTE{route}
    ROUTE -->|call subagent| BRIDGE[bridge<br/>tool_call → brief]
    ROUTE -->|reset_project| GATE[approval_gate<br/>HITL approval]
    ROUTE -->|none| END([END])

    BRIDGE -->|goto| PD[product_discovery<br/>subgraph]
    BRIDGE -->|goto| SA[system_architect<br/>subgraph]

    subgraph phase0 [Phase 0 subgraphs · internal conversation loop]
        PD
        SA
    end

    PD --> REVIEW[review]
    SA --> REVIEW
    GATE --> BRIDGE
    REVIEW --> ORC

    PD -.->|save| PRD[(prd.md)]
    SA -.->|save| ARCH[(architecture.md)]
```

- **orchestrator**: takes the conversation and decides which subagent to delegate to, via a
  tool-call. Runs `qwen3:8b`.
- **bridge**: converts the orchestrator's tool-call into a brief (HumanMessage) for the subagent
  and routes with `Command(goto=...)`. It uses LangGraph's **subgraph-as-node** mechanism directly,
  so a subagent's `interrupt` propagates to the parent automatically and the `resume` value flows
  back in automatically.
- **phase-0 subgraphs**: `product_discovery` (→ PRD) and `system_architect` (→ architecture doc).
  Each is a **conversational subgraph** cycling through an internal
  `model → save → check_done → wait_for_user` loop.
- **review / approval_gate**: returns to the orchestrator after reviewing an artifact; risky
  actions require human approval.

Key source: [src/agent.py](src/agent.py) (graph assembly),
[src/libs/subgraph.py](src/libs/subgraph.py) (conversational subgraph builder),
[src/subagents/planners/](src/subagents/planners/) (phase-0 agents).

---

## Hard problems solved

Each item is backed by code/traces; the design write-ups live in a separate blog series,
[**LangGraph Multi-Agent series**](https://bswebdev.hashnode.dev/series/lang-graph).

### 1. Cross-subagent state contamination → state isolation
With a shared `state["messages"]`, the orchestrator's handoff messages and tool_calls bled into
the planner's LLM input, causing the planner to introduce *itself* as the PM. I split subagents
into a separate `SubagentState` and drew a boundary with `RemoveMessage` in the `finalize` step to
stop parent-message contamination.
→ [src/subagents/state.py](src/subagents/state.py) · [libs/subgraph.py](src/libs/subgraph.py)

### 2. Subgraph resume restarted from scratch every time
The checkpointer wasn't passed down to the subgraph, so the user's reply vanished from `messages`
and the conversation reset to turn 1. I injected the checkpointer consistently down to the subgraph
and made FastAPI (async) and `langgraph dev` **share the same sqlite file**.
→ [src/agent.py:170](src/agent.py#L170)

### 3. `langgraph dev`'s sync-I/O block (blockbuster)
The dev middleware blocks synchronous I/O inside handlers, so the SqliteSaver connection failed.
I worked around it by opening the sqlite connection at **module load time** rather than inside
`graph()`, keeping it off the event loop. → [src/agent.py:150](src/agent.py#L150)

### 4. Making a stochastic 8B deterministic — isolating the done-check
When the planner (temp=0.5, divergent) made the `check_done` YES/NO call, it misjudged. I injected
a **separate temp=0 critic instance** (same model file) and stripped thinking tokens, making the
completion check deterministic.
→ [product_discovery/__init__.py](src/subagents/planners/product_discovery/__init__.py)

### 5. Save-validation gate & response post-processing
- `_validate_prd`: checks required sections exist and no placeholders remain, **blocking incomplete
  artifacts from being saved**. → [product_discovery/tools.py:34](src/subagents/planners/product_discovery/tools.py#L34)
- Response post-processing: strips `<think>` blocks, `🛑 [턴 종료]` markers, empty code fences, and
  greeting prefixes after turn 2, all via regex. → [src/libs/subgraph.py](src/libs/subgraph.py)
- `_sanitize_query`: normalizes the orchestrator's hallucinated honorifics (e.g. "대표님!") into a
  noun phrase. → [src/agent.py:17](src/agent.py#L17)

### 6. Hiding the save tool (dynamic tool binding)
Since the model ignored "don't save on turn 1", I made the **save tool conditionally bound** so it's
physically impossible to call. → [libs/subgraph.py](src/libs/subgraph.py) (`model_with_save`)

### 7. Model-selection log
A decision record of how `gemma4:e4b` (4B) failed at following Korean negative-instruction lists —
with LangSmith trace evidence — and the move to `qwen3:8b`. → [docs/plan/model-use.md](docs/plan/model-use.md)

---

## Tech stack

| Layer | Tech |
|-------|------|
| Orchestration | LangGraph (`StateGraph`, subgraph-as-node, `interrupt`/`Command`) |
| LLM runtime | Ollama (local) — `qwen3:8b` (orchestrator/planner), `deepseek-r1:8b` (critic candidate) |
| Serving | FastAPI (ASGI) + `langgraph dev` |
| State | SqliteSaver checkpointer (async/sync file sharing) |
| Observability | LangSmith tracing |
| Packaging | uv, Docker / docker-compose |

---

## Running it

```bash
# 1. Pull local models (Ollama required)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b

# 2. Environment variables
cp .env.example .env    # fill in LANGSMITH_API_KEY, MODEL_BASE_URL, etc.

# 3. Dev server
uv sync
uv run uvicorn src.main:app --reload
# or LangGraph Studio: uv run langgraph dev

# 4. (optional) containers
docker-compose up --build
```

---

## Implementation status vs roadmap

This repo deliberately narrows scope to **Phase 0 as a "finished product"** to gain depth. Given
the code-generation ceiling of an 8B local model, stretching all the way to Phase 1–6 (actual code
generation) would produce an "ambitious but non-working demo".

| Scope | Status |
|-------|--------|
| Phase 0 — Product Discovery (idea → PRD) | ✅ wired in code |
| Phase 0 — System Architect (PRD → architecture) | ✅ wired in code |
| Orchestrator routing · HITL approval gate · state isolation | ✅ wired in code |
| Phase 1–6 (build/QA/security/deploy agents) | 📐 persona designs only ([agents/](agents/)) · roadmap |
| Go gateway (SSE streaming BFF) · streaming web UI | 🚧 planned |

---

## License

[MIT](LICENSE)
