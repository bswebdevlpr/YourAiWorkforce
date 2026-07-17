"""LLM 호출 계측 하네스.

로컬 8B를 '조이는' 설계 결정(역할별 num_ctx, 가중치 공유, 짧은 판정 vs 긴 생성,
thinking 토큰 억제)을 **정성 주장이 아니라 숫자**로 뒷받침하기 위한 얇은 계측 레이어.

Ollama는 응답 metadata에 이미 다음 카운터를 실어 보낸다(단위: 나노초):
    prompt_eval_count / prompt_eval_duration   → prefill(입력 처리)
    eval_count / eval_duration                 → decode(토큰 생성)
    load_duration                              → 모델 로드(콜드스타트) 페널티
    total_duration                             → 벽시계

`create_chat_model`이 역할별로 이 핸들러를 하나씩 붙인다. 모델 인스턴스마다
자기 role/num_ctx/temperature를 알고 있으므로 run_id 상관관계 추적이 필요 없다.
모든 호출은 JSONL 한 줄로 append된다. 집계는 scripts/metrics_report.py.

끄려면: 환경변수 LLM_METRICS=0.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from src.libs.path import ROOT

_NS_PER_S = 1_000_000_000
_NS_PER_MS = 1_000_000

# 한국어 1자 ≈ 1.3 토큰(qwen 토크나이저 근사). 보이는 content의 토큰 수를 추정해
# '생성했지만 버려진(thinking) 토큰' 비율을 계산하는 용도. 정밀값이 아니라 지표.
_CHARS_TO_TOKENS = 1.3


def _metrics_enabled() -> bool:
    return os.getenv("LLM_METRICS", "1") not in ("0", "false", "False", "")


def _sink_path() -> Path:
    override = os.getenv("LLM_METRICS_PATH")
    if override:
        return Path(override)
    return ROOT / "metrics" / "llm_calls.jsonl"


def _estimate_tokens(text: str) -> int:
    return int(len(text) * _CHARS_TO_TOKENS)


@dataclass
class LLMCallMetric:
    """단일 LLM 호출의 계측 레코드."""

    ts: float  # epoch seconds
    role: str
    model: str
    num_ctx: int
    temperature: float
    reasoning: bool | None  # qwen3 thinking 모드 (None=기본 on, False=끔)

    # Ollama 원시 카운터
    prompt_tokens: int | None
    output_tokens: int | None
    load_ms: float | None
    prefill_ms: float | None
    decode_ms: float | None
    wall_ms: float | None
    done_reason: str | None

    # 파생 지표
    prefill_tok_s: float | None  # 입력 처리 처리량
    decode_tok_s: float | None  # 토큰 생성 처리량
    ttft_ms: float | None  # 첫 토큰까지 ≈ load + prefill
    visible_tokens: int | None  # 사용자에게 실제 노출된(추정) 토큰
    thinking_tokens: int | None  # 생성했지만 버려진(추정) 토큰
    thinking_ratio: float | None  # thinking / output — '조임' 여지의 크기
    cold_start: bool  # load_ms가 유의미하면 모델 로드가 발생한 콜


class _Sink:
    """스레드-세이프 append-only JSONL writer. FastAPI(async)와 langgraph dev가
    같은 파일에 쓸 수 있으므로 lock으로 라인 원자성만 보장한다."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._path: Path | None = None

    def write(self, record: dict[str, Any]) -> None:
        if self._path is None:
            self._path = _sink_path()
            self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")


_SINK = _Sink()


def _div(numer: float | None, denom: float | None) -> float | None:
    if not numer or not denom:
        return None
    return numer / denom


class LLMMetricsHandler(BaseCallbackHandler):
    """모델 인스턴스 1개당 1개. 자기 role/num_ctx/temperature를 알고 있다."""

    raise_error = False  # 계측이 실패해도 그래프 실행을 막지 않는다

    def __init__(
        self,
        *,
        role: str,
        model: str,
        temperature: float,
        num_ctx: int,
        reasoning: bool | None = None,
    ) -> None:
        self.role = role
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.reasoning = reasoning

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if not _metrics_enabled():
            return
        try:
            metric = self._build(response)
        except Exception:
            # 계측은 best-effort. 절대 호출 경로를 깨지 않는다.
            return
        _SINK.write(asdict(metric))

    def _build(self, response: LLMResult) -> LLMCallMetric:
        gen = response.generations[0][0]
        message = getattr(gen, "message", None)
        meta: dict[str, Any] = {}
        if message is not None:
            meta = dict(getattr(message, "response_metadata", None) or {})
        if not meta:
            meta = dict(getattr(gen, "generation_info", None) or {})

        prompt_tokens = meta.get("prompt_eval_count")
        output_tokens = meta.get("eval_count")
        prefill_ns = meta.get("prompt_eval_duration")
        decode_ns = meta.get("eval_duration")
        load_ns = meta.get("load_duration")
        total_ns = meta.get("total_duration")

        content = getattr(message, "content", "") if message is not None else ""
        visible = _estimate_tokens(content if isinstance(content, str) else "")
        thinking = None
        thinking_ratio = None
        if output_tokens:
            thinking = max(output_tokens - visible, 0)
            thinking_ratio = round(thinking / output_tokens, 3)

        load_ms = _ns_to_ms(load_ns)
        prefill_ms = _ns_to_ms(prefill_ns)

        return LLMCallMetric(
            ts=time.time(),
            role=self.role,
            model=self.model,
            num_ctx=self.num_ctx,
            temperature=self.temperature,
            reasoning=self.reasoning,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            load_ms=load_ms,
            prefill_ms=prefill_ms,
            decode_ms=_ns_to_ms(decode_ns),
            wall_ms=_ns_to_ms(total_ns),
            done_reason=meta.get("done_reason"),
            prefill_tok_s=_round(_div(prompt_tokens, _div(prefill_ns, _NS_PER_S))),
            decode_tok_s=_round(_div(output_tokens, _div(decode_ns, _NS_PER_S))),
            ttft_ms=_round(_sum(load_ms, prefill_ms)),
            visible_tokens=visible if output_tokens else None,
            thinking_tokens=thinking,
            thinking_ratio=thinking_ratio,
            # load가 50ms 이상이면 실질적으로 모델(가중치/컨텍스트) 로드가 일어난 콜
            cold_start=bool(load_ms and load_ms > 50),
        )


def _ns_to_ms(ns: float | None) -> float | None:
    if ns is None:
        return None
    return round(ns / _NS_PER_MS, 1)


def _sum(*vals: float | None) -> float | None:
    present = [v for v in vals if v is not None]
    return sum(present) if present else None


def _round(v: float | None, ndigits: int = 1) -> float | None:
    return round(v, ndigits) if v is not None else None


def snapshot_memory(base_url: str | None = None) -> list[dict[str, Any]]:
    """현재 Ollama에 상주 중인 모델의 메모리 스냅샷(/api/ps).

    반환: [{name, size_vram_gb, context_length, quantization}] — RAM 축 근거.
    """
    url = (base_url or os.getenv("MODEL_BASE_URL") or "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(f"{url}/api/ps", timeout=3) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []
    out = []
    for m in data.get("models", []):
        out.append(
            {
                "name": m.get("name"),
                "size_vram_gb": round((m.get("size_vram") or 0) / 1e9, 2),
                "context_length": m.get("context_length"),
                "quantization": (m.get("details") or {}).get("quantization_level"),
            }
        )
    return out
