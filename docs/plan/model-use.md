# 🚀 Local Multi-Agent LLM Stack (2026.04)

> **Target Hardware:** MacBook M4 (16GB Unified Memory)
> **Infrastructure:** Native Ollama (Model) + Docker (App & DB)

---

## 1. 최종 모델 라인업 (Ollama 공식 태그 기준)

| 역할 (Role)              | 추천 모델 (Ollama Tag) | 핵심 가치 (Why?) | 주요 특징                                        |
| :----------------------- | :--------------------- | :--------------- | :----------------------------------------------- |
| **Orchestrator & Coder** | `qwen3.5:9b`           | **신뢰성**       | 도구 호출(Tool Call) 및 JSON 출력 성공률 최상위  |
| **Planner**              | `gemma4:e4b`           | **창의성/맥락**  | 256K 컨텍스트, MatFormer 기반 경량 구동, 한국어·Vision·Audio 멀티모달 |
| **Critic**               | `deepseek-r1:8b`       | **논리/추론**    | 사고 과정(CoT)을 통한 비판적 사고 및 오류 탐지   |

---

## 2. 상세 운영 가이드

### 🧠 Orchestrator: Qwen 3.5 (9B)

- **용도:** 유저 요구사항 분석, 에이전트 워크플로우 제어, 상태(State) 업데이트 판단.
- **팁:** 전체 시스템의 '입' 역할을 수행하므로 항상 상주시킵니다. 지시 이행력이 매우 좋아 루프가 깨지지 않습니다.

### 📝 Planner: Gemma 4 (E4B)

- **용도:** 서비스 기획서 초안 작성, 상세 기능 명세서, 사용자 시나리오 설계.
- **팁:** MatFormer 아키텍처로 실제 8B 파라미터지만 4B 수준(~3GB) 메모리로 구동됩니다. Orchestrator/Critic과 동시 상주가 여유로워졌습니다.
- **강점:** 256K 컨텍스트와 Audio/Vision 입력 지원으로 긴 회의록·음성 메모 기반 기획이 가능합니다.

### ⚖️ Critic: DeepSeek-R1 (8B)

- **용도:** 기획서의 논리적 결함 체크, 유저 피드백의 기술적 해석, 최종 검수.
- **팁:** 일반적인 LLM과 달리 '사고 과정(CoT)'을 출력하므로, 왜 이 기획이 잘못되었는지 논리적으로 반박하는 능력이 탁월합니다.

---

## 3. 환경 구축 커맨드

터미널에서 아래 명령어를 순서대로 입력하여 모델 셋업을 완료하세요.

```bash
# 1. 오케스트레이터 설치
ollama pull qwen3.5:9b

# 2. 기획용 설치
ollama pull gemma4:e4b

# 3. 검수용 설치
ollama pull deepseek-r1:8b
```
