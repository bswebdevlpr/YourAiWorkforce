# Squeezing the local model — measured, not asserted

The README's core claim is *"don't trust the 8B, clamp it."* Clamping is about
**correctness**. This directory is about the other axis — **efficiency**: how hard the
local model is squeezed for latency, tokens, and memory on a 16GB machine, backed by
numbers instead of adjectives.

Everything here is reproducible from the instrumentation harness described below.

---

## 1. The instrumentation harness

Ollama already ships per-call counters in its response metadata (durations in nanoseconds):

| counter | meaning |
|---|---|
| `prompt_eval_count` / `prompt_eval_duration` | prefill — reading the input |
| `eval_count` / `eval_duration` | decode — generating tokens |
| `load_duration` | model/context load (cold-start penalty) |
| `total_duration` | wall clock |

[`src/libs/metrics.py`](../../src/libs/metrics.py) attaches a role-tagged LangChain
callback to every model created by `create_chat_model`, so the three call sites
(orchestrator · planner-gen · critic-done) are all captured from one chokepoint. Each call
appends one JSON line to `metrics/llm_calls.jsonl`; derived metrics (decode tok/s, TTFT,
thinking-token ratio, cold-start flag) are computed at write time.
[`scripts/metrics_report.py`](../../scripts/metrics_report.py) aggregates per role, and
`snapshot_memory()` reads `/api/ps` for the memory axis.

Disable with `LLM_METRICS=0`. Raw logs are gitignored; only the aggregated write-ups here
are committed.

**What one live run exposes (qwen3:8b, Q4_K_M, M4/16GB):**

| role | num_ctx | out_tok | wall | think_ratio | TTFT | vram |
|---|---|---|---|---|---|---|
| critic (done-check) | 4096 | 465 | 25.1s | **1.0** (all discarded) | 0.8s | 5.65 GB |
| planner (generation) | 20480 | 608 | 37.0s | 0.2 | **5.7s** | 6.96 GB |

Three design decisions become visible in one table:
- **num_ctx → TTFT**: 4096 prefills in 0.8s, 20480 in 5.7s. Per-role context sizing *is*
  per-role prefill-latency budgeting.
- **num_ctx → RAM**: the same model file costs 5.65 GB at ctx 4096 vs 6.96 GB at 20480.
  Context window is KV-cache memory; ~1.3 GB bought by a larger book on a 16 GB desk.
- **thinking waste**: the done-check's `think_ratio = 1.0` — a YES/NO answer where *every*
  generated token is discarded reasoning. This is the thread pulled in §2.

---

## 2. Case study — the done-check thinking budget

### The problem

`check_done` ([src/libs/nodes.py](../../src/libs/nodes.py)) asks the critic a single
YES/NO question: *did the user make an additional request?* qwen3 runs in **thinking
mode** by default — it generates a long `<think>…</think>` chain before answering. That
chain is stripped from the *output*, but the tokens are still generated, so the *latency
is already paid*. At ~20 tok/s on-device, a 465-token think block is ~25 seconds spent on
bytes the user never sees.

### The tempting (wrong) conclusion

Turning thinking off (`reasoning=False`) collapses a done-check from ~25s to ~0.3s and
from ~465 tokens to ~2. A single before/after even showed thinking answering *wrong*
(overthinking a trivial case). It looks like a free 50×+ win.

It isn't free — and a labeled eval ([scripts/eval_check_done.py](../../scripts/eval_check_done.py),
18 cases: 10 clear + 8 deliberately ambiguous, gold labels are the author's judgment and
the ambiguous ones are debatable) shows why.

### Result A — thinking on/off, original prompt

| mode | acc (all) | acc (clear) | acc (ambiguous) | wall (median) | out_tok (median) |
|---|---|---|---|---|---|
| thinking | 72% (13/18) | 90% (9/10) | **50% (4/8)** | 12.4 s | 196 |
| no-think | 61% (11/18) | 90% (9/10) | **25% (2/8)** | 0.28 s | 2 |

The instinct was right: on **ambiguous** cases, reasoning genuinely helps (50% vs 25%).
On **clear** cases it buys nothing (90% = 90%) and even introduces an overthinking failure.
Crucially, every one of no-think's ambiguous errors was the *same* direction —
`gold=NO → predicted YES`, i.e. **flattening an implicit request into "done."** A
systematic bias, not random noise.

### The real lever — task design, not inference compute

The fix for a systematic bias is not "think harder." Since a premature "done" (false YES)
is a costly error in a human-in-the-loop flow — the user loses the thread — while an extra
"anything else?" (false NO) is cheap, the prompt was rewritten to **bias toward *continue*
on any hint of a request, question, or hesitation** ([`CHECK_DONE_SYSTEM`](../../src/libs/nodes.py)).

### Result B — same (rewritten) prompt, on/off apples-to-apples

| mode | acc (all) | acc (clear) | acc (ambiguous) | wall (median) | out_tok (median) |
|---|---|---|---|---|---|
| thinking | 83% (15/18) | 100% (10/10) | 62% (5/8) | 13.6 s | 223 |
| no-think | **78% (14/18)** | **100% (10/10)** | 50% (4/8) | **0.28 s** | 2 |

- The **prompt rewrite lifted both modes ~15pp** (no-think 61→78, thinking 72→83) — a far
  bigger lever than thinking on/off (~5pp). It also erased thinking's overthinking miss on
  clear cases (→ 100%).
- With a good prompt, **thinking's entire remaining advantage is one ambiguous case**
  (`"아 그리고 모바일도"` — a trailing fragment), bought at **~48× the latency** (13.6 s vs
  0.28 s). Clear cases — which dominate the real check_done distribution — are a dead tie
  at 100%.
- Of no-think's 4 remaining errors, 2 now err toward *continue* (the safe direction, and
  arguably the labels are wrong); only 2 are genuine premature-completions, down from 6.

### Conclusion

> On this task, **prompt design + choosing the safe error direction beat inference-time
> compute** — at 48× lower latency and matched accuracy on the dominant (clear) case
> distribution. "Make the model think harder" lost to "specify the task correctly and
> cheaply, and make its failures fall in the safe direction."

That is the clamp/squeeze thesis in miniature: wrap the probabilistic component in a
deterministic, well-specified, cheap shell rather than paying the model to deliberate.

### Caveats (kept honest)

- n = 18, single run per case; thinking mode is non-deterministic, so its accuracy can vary
  run to run.
- Ambiguous labels are debatable — two of no-think's "errors" are cases where its answer is
  arguably more correct than the gold label.
- The eval feeds single isolated messages; the real node sees full conversation context,
  which likely makes judgments *easier* — so these are context-poor, worst-case numbers.

---

## 3. What's wired now

- Critics run `reasoning=False` (no-think) — [product_discovery](../../src/subagents/planners/product_discovery/__init__.py),
  [system_architect](../../src/subagents/planners/system_architect/__init__.py).
- `check_done` uses the safety-biased [`CHECK_DONE_SYSTEM`](../../src/libs/nodes.py)
  (ambiguous → continue).
- Generation calls keep thinking on (unchanged) — reasoning is worth paying for there.

## Reproduce

```bash
# per-call harness → aggregated table + memory snapshot
uv run python -m scripts.metrics_report

# done-check labeled eval (both modes; ~5 min for the thinking pass)
uv run python -m scripts.eval_check_done
uv run python -m scripts.eval_check_done --skip-thinking   # fast no-think-only iteration
```
