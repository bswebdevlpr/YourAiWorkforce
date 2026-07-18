# Gateway — the streaming BFF

A small Go service that sits in front of the Python LangGraph orchestrator and owns the
**client-facing protocol**. Stdlib only — `net/http`, goroutines, `context`, `embed`. No framework,
no third-party deps (`go.mod` has zero `require`s).

```
browser ──POST /chat──▶  Go gateway :8080  ──POST / (raw tokens)──▶  Python FastAPI :8000 ──▶ Ollama
        ◀─SSE events──         │            ──GET /state/:id────────▶
                               └─ serves the web UI (embedded)
```

**Why a separate service, not a byte proxy?** The Python stream can't say *why* it ended — a
completed turn and a graph paused at an `interrupt()` are byte-identical on the wire. The gateway
reconstructs that distinction out of band. Full write-up:
[engineering-notes #8](../docs/engineering-notes.md#8-the-python-stream-never-says-why-it-ended).

---

## Protocol

### Request — `POST /chat`

```json
{ "message": "…", "thread_id": "uuid", "type": "new" }
```

| `type` | when | meaning |
|--------|------|---------|
| `new` | first message of a thread | start a fresh conversation |
| `message` | thread is idle (not paused) | continue the conversation |
| `reply` | thread is paused at an interrupt | resume with a text answer |
| `complete` / `reject` | thread is paused at an interrupt | resume by ending / aborting the step |

The gateway passes `type` through to Python unchanged; Python decides `new`-input vs `Command(resume=…)`.

### Response — `text/event-stream`

| event | payload | meaning |
|-------|---------|---------|
| `token` | `{"text":"…"}` | a model token fragment — append to the current bubble |
| `interrupt` | `{"result":"…","options":["reply","complete","reject"]}` | graph paused; render an approval prompt |
| `done` | `{"reason":"end"}` | turn finished normally; re-open the input box |
| `error` | `{"message":"…"}` | upstream failure |

A turn ends with **exactly one** terminal event: `interrupt`, `done`, or `error`. After `interrupt`
the stream closes with no `done` — the next human reply is a fresh `POST /chat`, not a continuation.

### Upstream contract (what the gateway needs from Python)

- `POST /` — raw token stream (`text/event-stream` media type, but unframed token content).
- `GET /state/{thread_id}` — `{exists, interrupted, interrupt}`; read-only, drives the terminal-event
  decision. Added in [src/main.py](../src/main.py); the graph itself is untouched.

---

## Running

```bash
# 1. Python orchestrator must be up first (see repo README)
uv run uvicorn src.main:app --port 8000

# 2. Gateway + UI
cd gateway && go run .        # → http://localhost:8080

# override the upstream (default http://localhost:8000)
UPSTREAM_BASE=http://python-host:8000 go run .
```

The web UI ([static/index.html](static/index.html)) is baked into the binary with `//go:embed`, so a
production build is a single file with no asset paths to resolve:

```bash
go build -o gw . && ./gw
```

---

## How it was built (design log)

Built in thin vertical slices — each one runnable and tested before the next, each isolating one new
concept. This is the build order, kept as a record of the reasoning.

| # | Slice | Added | Go concept exercised | Key decision |
|---|-------|-------|----------------------|--------------|
| 1 | Walking skeleton | SSE server streaming from a fake token source | `net/http` routing · SSE framing · `http.Flusher` · `context` cancel via `select` | Prove the pipe end-to-end before touching Python |
| 2 | HTTP client | Relay from a separate mock upstream | `http.Client` · `io.Reader` · `defer Close()` | Isolate client-side streaming from Python/Ollama variables |
| 3 | Interrupt events | `upstreamEvent{Kind, Data}` on the channel; `interrupt` handling | typed channel payloads · `json.RawMessage` (defer parsing) | End the SSE turn on `interrupt`; don't also send `done` |
| 4 | Real Python | Swap mock for `:8000`; the protocol reconstruction | `resp.Body.Read` over `bufio.Scanner` · out-of-band state fetch | Python = graph engine, Go = wire protocol ([note #8](../docs/engineering-notes.md#8-the-python-stream-never-says-why-it-ended)) |
| 5 | Web UI | Embedded `fetch`+`ReadableStream` SSE client | `embed.FS` · `fs.Sub` · `http.FileServerFS` | `EventSource` can't POST → parse SSE by hand, same as the server side |

Two recurring lessons worth their own line:

- **Streaming means reassembly, on both ends.** Tokens arrive on boundaries that don't match event
  boundaries. The server reads raw bytes (`resp.Body.Read`); the browser buffers and splits on `\n\n`.
  A line scanner would stall until a newline that may never come.
- **`go run` leaves a zombie.** `pkill -f "go run ."` kills the parent but not the compiled child
  holding the port. During dev, `go build -o /tmp/gw && /tmp/gw` avoids the trap.

---

## Roadmap

Planned slices, ordered by interview-story value for a backend/systems portfolio. Each answers the
same question slice 4 first answered — *what can a BFF do that a byte proxy can't?*

| # | Slice | What it adds | Story it unlocks |
|---|-------|--------------|------------------|
| 6 | Middleware + lifecycle | request-id / logging / panic-recovery middleware; `signal.NotifyContext` graceful shutdown; `http.Server` + upstream timeouts | production-readiness, `http.Handler` composition |
| 7 | Ollama serialization | semaphore (buffered channel) capping concurrent upstream calls to 1, with a queue; `event: queued {position}` | backpressure at the service boundary for a real single-8B constraint |
| 8 | Streaming metrics | time-to-first-token + tokens/sec; `/metrics` in Prometheus text format | observability; TTFT is *the* latency metric for streaming LLM systems |

Not prioritized: session listing/restore and artifact-serving APIs. Useful for demo UX, but closer to
CRUD than to a systems story — deliberately behind #6–8.
