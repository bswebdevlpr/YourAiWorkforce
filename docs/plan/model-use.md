# 🚀 Local Multi-Agent LLM Stack (2026.05)

> **Target Hardware:** MacBook M4 (16GB Unified Memory)
> **Infrastructure:** Native Ollama (Model) + Docker (App & DB)

---

## 1. 최종 모델 라인업 (Ollama 공식 태그 기준)

| 역할 (Role)              | 추천 모델 (Ollama Tag) | 핵심 가치 (Why?) | 주요 특징                                        |
| :----------------------- | :--------------------- | :--------------- | :----------------------------------------------- |
| **Orchestrator & Coder** | `qwen3:8b`             | **신뢰성**       | 도구 호출(Tool Call) 및 JSON 출력 성공률 최상위  |
| **Planner**              | `qwen3:8b`             | **페르소나 추종력** | Orchestrator와 weight 공유로 메모리 추가 부담 거의 없음. 한국어 instruction-following 강력 |
| **Critic**               | `deepseek-r1:8b`       | **논리/추론**    | 사고 과정(CoT)을 통한 비판적 사고 및 오류 탐지   |

---

## 2. 상세 운영 가이드

### 🧠 Orchestrator: Qwen 3 (8B)

- **용도:** 유저 요구사항 분석, 에이전트 워크플로우 제어, 상태(State) 업데이트 판단.
- **팁:** 전체 시스템의 '입' 역할을 수행하므로 항상 상주시킵니다. 지시 이행력이 매우 좋아 루프가 깨지지 않습니다.

### 📝 Planner: Qwen 3 (8B)

- **용도:** 서비스 기획서 초안 작성, 상세 기능 명세서, 사용자 시나리오 설계.
- **팁:** Orchestrator와 동일 모델이라 Ollama가 weight를 공유 캐시 → 추가 메모리 부담 거의 없음.
- **강점:** 한국어 페르소나 톤·호칭·자칭 규칙 같은 negative instruction list 추종력이 4B 모델 대비 압도적.

### ⚖️ Critic: DeepSeek-R1 (8B)

- **용도:** 기획서의 논리적 결함 체크, 유저 피드백의 기술적 해석, 최종 검수.
- **팁:** 일반적인 LLM과 달리 '사고 과정(CoT)'을 출력하므로, 왜 이 기획이 잘못되었는지 논리적으로 반박하는 능력이 탁월합니다.

---

## 3. Planner 모델 변천사 & 결정 기록

### 2026.04 — `gemma4:e4b` 시도

- **선정 이유**: MatFormer 아키텍처로 8B 파라미터를 4B 메모리(~3GB)로 구동, 256K 컨텍스트, Vision/Audio 멀티모달.
- **실측 문제**: 한국어 페르소나 추종력 부족.
  - 시스템 프롬프트의 "PM/PO/매니저 자칭 금지" negative list를 무시하고 자기를 `"PM"`, `"제품 관리자"`, `"PO(Product Owner)"` 등으로 자칭.
  - "AI"로 자칭, "사용자님" 호칭 등 기본 호칭 규칙도 무시.
  - LangSmith trace `019ded8e-a8b9` 등에서 반복 재현됨.
- **원인**: 4B급 instruction-following 한계. 페르소나 본문의 PM 직무 어휘(PRD/MVP/P0/스코핑) 신호가 메타데이터·negative rule을 압도.

### 2026.05 — `qwen3:8b` 로 교체 (현재)

- **선정 이유**: Orchestrator와 동일 모델 → weight 공유로 메모리 추가 부담 최소. 8B에서 한국어 negative rule 추종력 확보.
- **검증 방법**: dev 재시작 후 LangSmith trace에서 PM/PO 자칭 재발 여부 확인.

### Fallback 후보 (1순위로도 부족할 시)

| 후보 | 메모리 (Q4) | 한국어 | Instruction Following | 비고 |
|---|---|---|---|---|
| `qwen3:14b` | ~8.3GB | 우수 | 매우 강함 | Qwen3-14B-Base가 Qwen2.5-32B 수준. Critic과 동시 상주 시 일부 swap 발생 가능 |
| `exaone3.5:7.8b` | ~5GB | 매우 우수 (LG 한국어 특화) | 보통-강함 | 한국어 페르소나 자연스러움 가능성 ↑. PRD 같은 구조화 출력 안정성은 시험 필요 |

### 후보에서 제외된 모델

- **`qwen3.6` (27B/35B-A3B, 2026.04 release)**: 14B 변형 없음. 27B는 16GB에 무리.
- **`exaone-4.0` / `exaone-4.5` (32B/33B, 2025.07~2026.04)**: 16GB 메모리 한계 초과.
- **`gemma3:12b`**: 한국어 출력에 로마자 자동 첨부 버그 보고됨 ([google-deepmind/gemma#268](https://github.com/google-deepmind/gemma/issues/268)).
- **`llama3.3:8b`**: 한국어 품질이 Qwen3 대비 약함.

---

## 4. 환경 구축 커맨드

터미널에서 아래 명령어를 순서대로 입력하여 모델 셋업을 완료하세요.

```bash
# 1. 오케스트레이터 & 기획용 (동일 모델, 1회 pull로 둘 다 커버)
ollama pull qwen3:8b

# 2. 검수용 설치
ollama pull deepseek-r1:8b
```
