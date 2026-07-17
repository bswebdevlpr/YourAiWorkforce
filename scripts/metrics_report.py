"""metrics/llm_calls.jsonl 을 역할별 표로 집계한다.

사용:
    uv run python -m scripts.metrics_report                 # 기본 경로 집계
    uv run python -m scripts.metrics_report --path x.jsonl  # 다른 파일
    uv run python -m scripts.metrics_report --md            # 마크다운 표(README 붙여넣기용)

각 역할(orchestrator / planner:*:gen / critic:*:done)이 확률적 8B를 어떻게 다르게
'조이는지'를 숫자로 보여준다:
  - decode_tok_s   : 토큰 생성 처리량
  - ttft_ms        : 첫 토큰까지(≈ load + prefill) — num_ctx가 클수록 커진다
  - thinking_ratio : 생성했지만 버려진 토큰 비율 — 짧은 판정 호출일수록 낭비가 크다
  - cold_start     : 모델 로드가 발생한 콜(콜드스타트 페널티)
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from src.libs.metrics import snapshot_memory
from src.libs.path import ROOT


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _mean(vals: list[float]) -> float | None:
    vals = [v for v in vals if v is not None]
    return round(statistics.mean(vals), 1) if vals else None


def _median(vals: list[float]) -> float | None:
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 1) if vals else None


COLUMNS = [
    ("role", "role"),
    ("n", None),
    ("num_ctx", None),
    ("decode_tok/s", "decode_tok_s"),
    ("ttft_ms(med)", "ttft_ms"),
    ("out_tok(med)", "output_tokens"),
    ("think_ratio", "thinking_ratio"),
    ("wall_ms(med)", "wall_ms"),
    ("cold", None),
]


def _aggregate(rows: list[dict]) -> list[dict]:
    by_role: dict[str, list[dict]] = {}
    for r in rows:
        by_role.setdefault(r["role"], []).append(r)

    out = []
    for role, group in sorted(by_role.items()):
        out.append(
            {
                "role": role,
                "n": len(group),
                "num_ctx": group[-1].get("num_ctx"),
                "decode_tok/s": _mean([g.get("decode_tok_s") for g in group]),
                "ttft_ms(med)": _median([g.get("ttft_ms") for g in group]),
                "out_tok(med)": _median([g.get("output_tokens") for g in group]),
                "think_ratio": _mean([g.get("thinking_ratio") for g in group]),
                "wall_ms(med)": _median([g.get("wall_ms") for g in group]),
                "cold": sum(1 for g in group if g.get("cold_start")),
            }
        )
    return out


def _render_table(agg: list[dict], markdown: bool) -> str:
    headers = [c[0] for c in COLUMNS]
    body = [[_fmt(row.get(h)) for h in headers] for row in agg]

    if markdown:
        lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        lines += ["| " + " | ".join(cells) + " |" for cells in body]
        return "\n".join(lines)

    widths = [max(len(headers[i]), *(len(r[i]) for r in body)) if body else len(headers[i]) for i in range(len(headers))]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    lines = [fmt.format(*headers), fmt.format(*["-" * w for w in widths])]
    lines += [fmt.format(*r) for r in body]
    return "\n".join(lines)


def _fmt(v) -> str:
    if v is None:
        return "-"
    return str(v)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=str(ROOT / "metrics" / "llm_calls.jsonl"))
    parser.add_argument("--md", action="store_true", help="마크다운 표로 출력")
    args = parser.parse_args()

    rows = _load(Path(args.path))
    if not rows:
        print(f"계측 데이터 없음: {args.path}\n(그래프를 한 번 돌리면 llm_calls.jsonl 이 쌓인다)")
        return

    agg = _aggregate(rows)
    print(f"# LLM 호출 계측 — 총 {len(rows)}콜, {len(agg)}개 역할\n")
    print(_render_table(agg, markdown=args.md))

    mem = snapshot_memory()
    if mem:
        print("\n## 현재 상주 모델 (Ollama /api/ps)")
        for m in mem:
            print(
                f"  {m['name']}  vram={m['size_vram_gb']}GB  "
                f"ctx={m['context_length']}  quant={m['quantization']}"
            )
        total = round(sum(m["size_vram_gb"] for m in mem), 2)
        print(f"  합계 상주 메모리: {total}GB")


if __name__ == "__main__":
    main()
