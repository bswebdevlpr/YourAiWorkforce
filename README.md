# YourAiWorkforce — Local 8B LLM Multi-Agent Orchestration

> **In one line**: a multi-agent planning pipeline that tames a *stochastic* 8B local
> model into behaving *deterministically enough to trust* — running entirely on a 16GB
> MacBook at **zero API cost**. A founder's rough idea → structured artifacts (PRD + architecture doc).

One orchestrator routes work to specialist subagents. A human approves each step. Every model call
runs on a local [Ollama](https://ollama.com) model — Phase 0 runs entirely on `qwen3:8b` (orchestrator,
planner, and a temp=0 critic instance) — no API, no cost, nothing leaves the machine.

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

Two services. The Go gateway owns the **client-facing protocol**; the Python service owns the
**graph**. The split is not cosmetic — see [why the gateway exists](docs/engineering-notes.md#8-the-python-stream-never-says-why-it-ended).

```mermaid
flowchart LR
    B["browser<br/>(SSE client)"]
    G["Go gateway :8080<br/>protocol · streaming · UI"]
    P["Python FastAPI :8000<br/>LangGraph orchestrator"]
    O["Ollama<br/>qwen3:8b (local)"]

    B -->|"POST /chat"| G
    G -->|"event: token / interrupt / done"| B
    G -->|"POST / (raw token stream)"| P
    G -->|"GET /state/:thread_id"| P
    P --> O
```

Inside the Python service, the graph itself:

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

## Engineering highlights

The harder problems this project actually turned on. Full write-ups, code, and traces →
**[docs/engineering-notes.md](docs/engineering-notes.md)**.

- **State isolation across a subgraph boundary** — strip a subagent's internal turns from the
  parent thread with `RemoveMessage`, while keeping LangGraph's native interrupt propagation.
- **A deterministic done-check, then measured** — a temp=0 critic with reasoning off and a
  safety-biased prompt matches thinking-mode accuracy at ~48× lower latency; prompt design beat
  inference-time compute ([numbers](docs/metrics/)).
- **Reconstructing why the stream ended** — the Python token stream is byte-identical whether a
  turn finished or paused for approval, so the Go gateway makes a second state call and emits
  explicit `interrupt`/`done` events. The load-bearing reason the gateway exists.
- **Making an illegal action impossible** — dynamic tool binding so the model physically *can't*
  call `save` before it's allowed, instead of asking it not to.

---

## Tech stack

| Layer | Tech |
|-------|------|
| Orchestration | LangGraph (`StateGraph`, subgraph-as-node, `interrupt`/`Command`) |
| LLM runtime | Ollama (local) — `qwen3:8b` for all Phase 0 roles (`deepseek-r1:8b` evaluated as critic, rejected — see [model log](docs/plan/model-use.md)) |
| Serving | FastAPI (ASGI) + `langgraph dev` |
| Gateway / BFF | Go (stdlib only — `net/http`, goroutines, `context`, `embed`) |
| Client protocol | SSE — `token` / `interrupt` / `done` / `error` (designed at the gateway) |
| State | SqliteSaver checkpointer (async/sync file sharing) |
| Observability | LangSmith tracing |
| Packaging | uv, Docker / docker-compose |

---

## Running it

```bash
# 1. Pull the local model (Ollama required) — Phase 0 runs entirely on qwen3:8b
ollama pull qwen3:8b

# 2. Environment variables
cp .env.example .env    # fill in LANGSMITH_API_KEY, MODEL_BASE_URL, etc.

# 3. Python orchestrator (port 8000)
uv sync
uv run uvicorn src.main:app --port 8000
# or LangGraph Studio: uv run langgraph dev

# 4. Go gateway + web UI (port 8080)
cd gateway && go run .
# then open http://localhost:8080
# override the upstream with UPSTREAM_BASE (default: http://localhost:8000)

# 5. (optional) containers
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
| Go gateway — SSE relay of the `interrupt`/`resume` protocol | ✅ wired in code ([gateway/](gateway/)) |
| Go gateway — thin streaming web UI | ✅ wired in code ([gateway/static/](gateway/static/)) |
| Go gateway — session management · artifact-serving API | 🚧 planned |

**See it actually run** → [docs/samples/](docs/samples/) holds a real, unedited PRD generated
end-to-end by the `product_discovery` agent (with the model's rough edges left in, documented honestly).

---

## How this was built

Pair-programmed with [Claude Code](https://claude.com/claude-code). The architecture, the
decisions, and the trade-offs documented here are mine; much of the implementation was AI-assisted.

## License

**All rights reserved.** This repository is public for portfolio/demonstration purposes only —
you may read the source to evaluate the work, but no license is granted to reuse, copy, modify, or
redistribute it. See [LICENSE](LICENSE).
