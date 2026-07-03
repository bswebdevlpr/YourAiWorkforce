# 🚀 Local Multi-Agent LLM Stack (2026.05)

> **Target Hardware:** MacBook M4 (16GB Unified Memory)
> **Infrastructure:** Native Ollama (model) + Docker (app & DB)

---

## 1. Final model lineup (Ollama official tags)

| Role                     | Recommended model (Ollama tag) | Core value | Key traits |
| :----------------------- | :----------------------------- | :--------- | :--------- |
| **Orchestrator & Coder** | `qwen3:8b`                     | **Reliability** | Top-tier success rate on tool calls and JSON output |
| **Planner**              | `qwen3:8b`                     | **Persona adherence** | Shares weights with the orchestrator → almost no extra memory. Strong Korean instruction-following |
| **Critic**               | `deepseek-r1:8b`              | **Logic / reasoning** | Critical thinking and error detection via chain-of-thought |

---

## 2. Detailed operating guide

### 🧠 Orchestrator: Qwen 3 (8B)

- **Use:** parse user requirements, control the agent workflow, decide state updates.
- **Tip:** it's the system's "mouth", so keep it resident at all times. Instruction-following is
  very good, so the loop doesn't break.

### 📝 Planner: Qwen 3 (8B)

- **Use:** service-plan drafts, detailed feature specs, user-scenario design.
- **Tip:** same model as the orchestrator, so Ollama shares the weight cache → almost no extra memory.
- **Strength:** far better than 4B models at following negative-instruction lists for Korean persona
  tone, honorifics, and self-reference rules.

### ⚖️ Critic: DeepSeek-R1 (8B)

- **Use:** check plans for logical flaws, technically interpret user feedback, final review.
- **Tip:** unlike a typical LLM it emits its chain-of-thought, so it's excellent at logically
  arguing *why* a plan is wrong.

---

## 3. Planner model history & decision log

### 2026.04 — tried `gemma4:e4b`

- **Why chosen**: MatFormer architecture runs an 8B-parameter model in ~4B (~3GB) of memory, 256K
  context, vision/audio multimodal.
- **Observed problem**: weak Korean persona adherence.
  - Ignored the system prompt's "don't call yourself PM/PO/manager" negative list and referred to
    itself as `"PM"`, `"product manager"`, `"PO (Product Owner)"`, etc.
  - Also ignored basic honorific rules — called itself "AI", addressed the user as "사용자님", etc.
  - Reproduced repeatedly in LangSmith traces (e.g. `019ded8e-a8b9`).
- **Cause**: the instruction-following ceiling of a 4B-class model. The PM job vocabulary in the
  persona body (PRD/MVP/P0/scoping) overwhelmed the metadata and negative rules.

### 2026.05 — switched to `qwen3:8b` (current)

- **Why chosen**: same model as the orchestrator → weight sharing minimizes extra memory. At 8B it
  reliably follows Korean negative rules.
- **Validation**: restart dev and check LangSmith traces for any recurrence of PM/PO self-reference.

### Fallback candidates (if the primary is still insufficient)

| Candidate | Memory (Q4) | Korean | Instruction following | Notes |
|---|---|---|---|---|
| `qwen3:14b` | ~8.3GB | good | very strong | Qwen3-14B-Base ≈ Qwen2.5-32B level. Some swap possible when co-resident with the critic |
| `exaone3.5:7.8b` | ~5GB | excellent (LG Korean-specialized) | fair–strong | Higher chance of natural Korean persona. Stability of structured output like PRDs needs testing |

### Models ruled out

- **`qwen3.6` (27B/35B-A3B, 2026.04 release)**: no 14B variant. 27B is too much for 16GB.
- **`exaone-4.0` / `exaone-4.5` (32B/33B, 2025.07–2026.04)**: exceeds the 16GB memory limit.
- **`gemma3:12b`**: reported bug auto-appending romanization to Korean output ([google-deepmind/gemma#268](https://github.com/google-deepmind/gemma/issues/268)).
- **`llama3.3:8b`**: Korean quality weaker than Qwen3.

---

## 4. Setup commands

Run the commands below in order to finish the model setup.

```bash
# 1. Orchestrator & planner (same model — one pull covers both)
ollama pull qwen3:8b

# 2. Critic
ollama pull deepseek-r1:8b
```
