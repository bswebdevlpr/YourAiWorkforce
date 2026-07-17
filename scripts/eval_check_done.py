"""check_done(완료 판정) — thinking on/off 정확도·지연 eval.

목적: "판정 호출의 thinking을 꺼도 정확도가 유지되는가?"를 4케이스 느낌이 아니라
라벨링된 셋으로 검증한다. 계측 하네스가 지연을 자동으로 잡으므로, 여기선 정답 라벨만
얹어 정확도 축을 붙인다.

판정 규약(src/libs/nodes.py check_done과 동일):
  system: "추가 요청이 명시적으로 있으면 NO, 없으면 YES 한 단어로만"
  verdict: <think> 제거 후 "NO"가 있으면 NO(=추가작업 필요), 없으면 YES(=완료)

gold 라벨은 저자 판단이다. clear는 이견이 거의 없지만 ambiguous는 논쟁 여지가 있음을
전제로 둔다 — 애매 구간이야말로 thinking on/off가 갈릴 수 있는 지점이라 일부러 넣었다.

사용:
    uv run python -m scripts.eval_check_done
"""

from __future__ import annotations

import argparse
import re
import statistics

from langchain_core.messages import HumanMessage, SystemMessage

from src.libs.model import create_chat_model

# 프로덕션 판정 프롬프트를 그대로 import — 복사본이 아니라 실물을 테스트한다.
from src.libs.nodes import CHECK_DONE_SYSTEM as JUDGE_SYSTEM

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# (사용자 발화, gold, 카테고리)  gold: YES=완료(추가요청 없음) / NO=추가요청 있음
DATASET = [
    # ---- clear: 추가 요청 없음 → YES ----
    ("좋아요, 저장해주세요", "YES", "clear"),
    ("네 좋습니다", "YES", "clear"),
    ("완벽해요, 이대로 진행하죠", "YES", "clear"),
    ("네 맞아요 그렇게 해주세요", "YES", "clear"),
    ("이 정도면 충분한 것 같아요", "YES", "clear"),
    # ---- clear: 명시적 추가 요청 → NO ----
    ("결제 기능도 추가해주세요", "NO", "clear"),
    ("로그인 기능도 넣어주세요", "NO", "clear"),
    ("가격을 3만원으로 바꿔주세요", "NO", "clear"),
    ("타겟 사용자를 20대 여성으로 수정해주세요", "NO", "clear"),
    ("푸시 알림 기능도 있으면 좋겠어요", "NO", "clear"),
    # ---- ambiguous: 라벨 논쟁 여지 있음 ----
    ("음 그건 나중에 생각해볼게요", "YES", "ambiguous"),  # 보류 = 지금 할 요청 아님
    ("흠 글쎄요 잘 모르겠네요", "YES", "ambiguous"),  # 불확실 표현, 액션 요청 아님
    ("이대로도 괜찮은데 혹시 더 넣을 게 있을까요?", "NO", "ambiguous"),  # 제안 요청
    ("좋은데 결제 흐름은 어떻게 되나요?", "NO", "ambiguous"),  # 구체화 요청성 질문
    ("네 근데 보안은 좀 신경 써주세요", "NO", "ambiguous"),  # 부드러운 추가 요청
    ("완료된 것 같은데 한 번만 다시 검토해줄래요?", "NO", "ambiguous"),  # 재검토 요청
    ("그냥 알아서 잘 정리해주세요", "NO", "ambiguous"),  # 추가 작업 위임
    ("아 그리고 모바일도", "NO", "ambiguous"),  # 미완결 추가 요청
]


def verdict_of(content: str) -> str:
    cleaned = _THINK_RE.sub("", content or "").strip().upper()
    return "NO" if "NO" in cleaned else "YES"


def run_mode(label: str, reasoning: bool | None) -> dict:
    # LLM_METRICS는 프로덕션 파일 오염 방지를 위해 이 스크립트에선 끄고, 지연은
    # response_metadata에서 직접 읽는다(하네스와 동일 소스).
    model = create_chat_model(
        "qwen3:8b", temperature=0.0, num_ctx=4096,
        role=f"eval:check_done:{label}", reasoning=reasoning,
    )
    rows = []
    print(f"\n=== {label} (reasoning={reasoning}) ===")
    for msg, gold, cat in DATASET:
        r = model.invoke([SystemMessage(JUDGE_SYSTEM), HumanMessage(msg)])
        pred = verdict_of(r.content)
        md = r.response_metadata or {}
        wall_ms = round((md.get("total_duration", 0)) / 1e6, 1)
        out_tok = md.get("eval_count")
        ok = pred == gold
        rows.append({"cat": cat, "gold": gold, "pred": pred, "ok": ok,
                     "wall_ms": wall_ms, "out_tok": out_tok, "msg": msg})
        mark = "✓" if ok else "✗"
        print(f"  {mark} [{cat:9}] gold={gold} pred={pred}  {wall_ms:>8.0f}ms  {out_tok:>4}tok  {msg}")
    return {"label": label, "rows": rows}


def _acc(rows: list[dict], cat: str | None = None) -> str:
    sub = [r for r in rows if cat is None or r["cat"] == cat]
    if not sub:
        return "-"
    n_ok = sum(r["ok"] for r in sub)
    return f"{n_ok}/{len(sub)} ({round(100*n_ok/len(sub))}%)"


def _median(rows: list[dict], key: str) -> float:
    return round(statistics.median([r[key] for r in rows]), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-thinking", action="store_true",
        help="느린 thinking 패스를 건너뛰고 no-think만 (프롬프트 튜닝 반복용)",
    )
    args = parser.parse_args()

    off = run_mode("no-think", reasoning=False)
    results = [off]
    if not args.skip_thinking:
        results.insert(0, run_mode("thinking", reasoning=None))

    print("\n\n# 요약 — check_done\n")
    hdr = ["mode", "acc(all)", "acc(clear)", "acc(ambig)", "wall_ms(med)", "out_tok(med)"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join(["---"] * len(hdr)) + "|")
    for res in results:
        r = res["rows"]
        print("| " + " | ".join([
            res["label"],
            _acc(r), _acc(r, "clear"), _acc(r, "ambiguous"),
            str(_median(r, "wall_ms")), str(_median(r, "out_tok")),
        ]) + " |")

    if len(results) == 2:
        # 불일치(두 모드가 갈린) 케이스 — 여기가 판단이 실제로 갈리는 지점
        print("\n## 두 모드가 갈린 케이스")
        on_map = {r["msg"]: r for r in results[0]["rows"]}
        any_diff = False
        for ro in off["rows"]:
            rn = on_map[ro["msg"]]
            if ro["pred"] != rn["pred"]:
                any_diff = True
                print(f"  gold={ro['gold']} | no-think={ro['pred']} thinking={rn['pred']} | {ro['msg']}")
        if not any_diff:
            print("  (없음 — 두 모드의 판정이 모든 케이스에서 동일)")

    # no-think 오답 목록 — 프롬프트 튜닝의 타깃
    print("\n## no-think 오답")
    wrong = [r for r in off["rows"] if not r["ok"]]
    if not wrong:
        print("  (없음)")
    for r in wrong:
        print(f"  gold={r['gold']} pred={r['pred']} | [{r['cat']}] {r['msg']}")


if __name__ == "__main__":
    main()
