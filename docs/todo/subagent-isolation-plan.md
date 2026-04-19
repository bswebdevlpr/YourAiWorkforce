# 서브에이전트 독립 thread + 브리핑 기반 컨텍스트 전파 리팩토링 계획

## 배경 및 목표

현재: parent 그래프의 단일 AsyncSqliteSaver가 서브그래프에도 전파 → 모든 대화가 parent thread 하나에 누적. 서브에이전트 간 state 공유로 역할 경계 흐려짐, 토큰 낭비.

목표:
1. 각 서브에이전트가 독립 thread_id 네임스페이스 + 영속 memory
2. Orchestrator만 전체 맥락 보관, 서브에이전트에는 "브리핑 패킷"만 전달
3. **Cross-subagent consultation** 지원 (방식 A: 단발 Q&A 중계)
4. 장기: **Meeting mode** (방식 B: 다자 대화)

---

## 설계 결정 (확정)

| 쟁점 | 결정 | 근거 |
|---|---|---|
| 1. 체크포인터 분리 | **단일 sqlite + 다른 thread_id** | 운영 단순. 단일 AsyncSqliteSaver를 parent + 모든 subagent가 공유, thread_id만 다르게 |
| 2. 서브그래프 호출 구조 | **bridge 노드가 외부 ainvoke** | subgraph를 parent 노드에서 제거. state 완전 격리 |
| 3. 브리핑 생성 방식 | **템플릿 기반** | tool schema 확장으로 orchestrator LLM이 직접 구성. LLM 요약은 추후 업그레이드 |
| 4. Interrupt 라우팅 | **parent bridge가 interrupt passthrough** | bridge가 subgraph astream 중 interrupt 감지 → parent도 `interrupt()`로 pause |
| 5. 재진입 thread 복원 | **parent state `_subagent_threads` registry** | dict[str, str] (name → thread_id). 새 호출=uuid4, 재호출=기존 |
| 6. 반환값 병합 | **요약 ToolMessage만 parent로** | subgraph last AIMessage 내용 + artifact 경로만 parent messages에 기록 |

---

## Phase 분할 (스코프 재조정)

### Phase B1 — MVP (이번 착수)
독립 thread + 브리핑 + interrupt passthrough. 여기까지 돌아가면 사용자 요구의 80% 해결.

### Phase B2 — 방식 A (consult)
서브에이전트 간 단발 Q&A 중계. Phase B1 운영 확인 후 착수.

### Phase B3 — 방식 B (meeting mode)
다자 대화 모드. **Phase B2 운영 2~3주 후 실제 수요 재평가 후 결정**. 안 쓰면 스킵.

### Phase B4 — 장기
Memory 요약/압축, Observability 강화.

---

## Tasks

### Phase B1

#### Task 1: State 스키마 확장 `[L1 / haiku]`
- **파일**: `src/state.py`
- **내용**:
  - `_session` 네임스페이스로 묶는 리팩토링 고려 (필드 산재 방지)
  - 추가 필드:
    - `_subagent_threads: Annotated[dict[str, str], operator.or_]`
    - `_active_subagent: str`
    - `_active_subagent_thread: str`
  - 기존 `_approved_subagents` 유지
- **선행**: 없음

#### Task 2: Tool schema 확장 `[L1 / haiku]`
- **파일**: `src/subagents/__init__.py`
- **내용**: `SUBAGENT_TOOLS` parameters에 다음 추가
  - `context_hints: string` — 이번 작업에 필요한 결정/맥락 요약
  - `artifact_refs: array<string>` — 참고할 산출물 경로 목록
  - `required`는 `query`만 유지
- **선행**: 없음 (Task 1과 병렬)

#### Task 3: Subgraph factory + checkpointer 주입 `[L2 / sonnet]`
- **파일**: `src/libs/subgraph.py`, `src/subagents/spec.py`, `src/subagents/planners/`, `src/main.py`
- **내용**:
  - `SubagentSpec.graph` → `SubagentSpec.graph_factory: Callable[[Checkpointer], CompiledGraph]`
  - `build_conversational_subgraph(..., checkpointer=None)` 추가
  - main.py lifespan에서 checkpointer로 parent + 모든 subagent graph compile → `app.state.subagents: dict[str, CompiledGraph]`
  - 기존 `.graph` 참조 전수조사 필요
- **선행**: 없음 (Task 1/2와 병렬)

#### Task 4: Bridge 노드 재구성 — 핵심 `[L3 / opus, 메인 직접]`
- **파일**: `src/agent.py` (bridge 재작성), `src/libs/nodes.py` (helper)
- **내용**:
  1. async 노드로 변경
  2. tool_call args에서 `query/context_hints/artifact_refs` 추출 → 브리핑 HumanMessage 템플릿
  3. `_subagent_threads.get(name)` 조회, 없으면 `uuid4()` 발급
  4. `app.state.subagents[name].ainvoke(..., config={"configurable": {"thread_id": sub_tid}})` 호출
     - 첫 호출/완료 후 재호출: 새 input 주입
     - `_active_subagent_thread == sub_tid`: `Command(resume=payload)` 주입
  5. 결과 분기:
     - interrupt로 끝: parent에서 `interrupt()` 호출 → pause
     - `is_done=True`: last AIMessage 요약 → `ToolMessage(tool_call_id=...)` parent 추가 → clear active → goto=review
- **⚠ Fallback 전략 (명시 필수)**:
  - 외부 ainvoke + 수동 interrupt passthrough가 LangGraph 1.1.2에서 안정적이지 않으면
  - **"subgraph를 parent 노드로 유지 + state schema 분리"** 로 축소 (state 격리만 달성, thread 독립 포기)
  - feature 브랜치로 격리하여 실패 시 롤백 쉽게
- **선행**: Task 1, Task 3

#### Task 5: Parent 그래프 배선 정리 `[L2 / sonnet]`
- **파일**: `src/agent.py`
- **내용**:
  - `graph()` 에서 `for name, spec in SUBAGENT_REGISTRY.items(): builder.add_node(name, spec.graph)` 제거
  - `builder.add_edge(name, "review")` 루프 제거 → bridge가 완료 시 직접 review로 goto
  - conditional_edges 단순화
  - approval_gate는 유지 (승인 시 Command update에 thread 등록은 bridge 위임)
- **선행**: Task 4

#### Task 6: main.py resume 라우팅 보강 `[L2 / sonnet]`
- **파일**: `src/main.py`
- **내용**:
  - parent snapshot.values에 `_active_subagent`가 있는데 `type="new"`면 400
  - 그 외 기존 로직 유지 (parent에만 resume 전달, bridge 내부 passthrough)
  - TestClient 시나리오 검증
- **선행**: Task 5

#### 🔍 Task 6.5: E2E 검증 체크포인트
- **내용**: Task 6 이후 다음 시나리오 수동 검증 후 커밋 고정
  - 서브에이전트 첫 호출 → interrupt → resume → 완료
  - 같은 서브에이전트 재호출 시 기존 thread 복원 확인
  - 서로 다른 서브에이전트 호출 시 state 격리 확인
  - reset_project 이후 동작
  - type="new" → 새 thread
- **선행**: Task 6

---

### Phase B2 (후속)

#### Task 7: consult tool — 방식 A `[L2 / sonnet]`
- **내용**:
  - `consult_subagent(target, question, return_to)` tool 추가
  - target subagent thread에 일회성 ainvoke (interrupt 없음 — **consultation mode 플래그**로 wait_for_user 스킵)
  - 답변 주입 규약: **User 승인 방식** (orchestrator가 답변을 user에게 보고 → user가 활성 subagent에 전달 지시)
- **Task 4 영향**: bridge가 "background consultation" 경로도 지원하도록 확장

---

### Phase B3 (수요 확인 후)

#### Task 8: meeting mode — 방식 B `[L3 / opus]`
- **내용**:
  - `start_meeting(participants)` / `end_meeting()` tool
  - parent state `_meeting: {participants, log}` 필드
  - Turn-taking: **User-driven** (User가 다음 발언자 지정)
  - Meeting 진입이 곧 참여자 승인 시점 (approval_gate 통합)
  - 종료 시 meeting 요약을 참여자 thread들에 ToolMessage로 push
- **실사용 수요 재평가 후 착수 결정**

---

### Phase B4 (장기)

- **Memory 요약/압축**: N 턴 초과 시 요약 교체. LangGraph MessagePruner 활용
- **Observability**: thread_id, subagent_name, phase 기반 구조화 로깅. langsmith tracing 연동

---

## 실행 순서

```
1라운드 병렬: Task 1 (L1) + Task 2 (L1) + Task 3 (L2)
       ↓
2라운드:    Task 4 (L3, 메인 직접, feature 브랜치)
       ↓
3라운드:    Task 5 (L2) → Task 6 (L2)
       ↓
           Task 6.5 검증 체크포인트
       ↓
Phase B2:   Task 7 (L2)
       ↓
Phase B3:   Task 8 (L3) — 수요 재확인 후
```

---

## 예상 모델 사용량 (Phase B1 기준)
- L1 (haiku): 2개
- L2 (sonnet): 3개
- L3 (opus): 1개 (메인 직접)

---

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| **Task 4 interrupt passthrough 실패** | 전체 blocker | Fallback: parent 노드 유지 + state schema 분리로 축소 |
| **SUBAGENT_REGISTRY `.graph` 기존 참조** | Task 3 영향 | 착수 전 grep 전수조사 |
| **Memory 누적 → context 초과** | 장기 | Phase B4 압축 전략 |
| **subagent ainvoke 실패 처리 미정의** | 런타임 에러 | Task 4에 에러 복구 로직 포함 |

---

## Phase B1 착수 전 합의 항목 (확정)

### 1. State 네임스페이스 — **개별 필드 유지 (현행 방식)**
- `_session: dict` 통합 방식은 중첩 dict 리듀서 제어가 까다로워 제외
- Phase B1에서 추가되는 `_subagent_threads`, `_active_subagent`, `_active_subagent_thread`는 기존 필드와 동일 패턴으로 개별 추가
- 필드별 리듀서 명확성 우선 (list=add, str=replace, dict=operator.or_)

### 2. 브리핑 템플릿 — **3섹션 고정 + artifact는 경로만**
```
## 이번 작업 목표
{query}

## 고려할 맥락
{context_hints}

## 참고 산출물
{artifact_refs 경로 목록}
```
- 파일 내용은 bridge에서 주입하지 않음. subagent 쪽 `_artifact_cache`가 필요 시 로드
- 섹션 라벨 한국어 유지 (persona 전반이 한국어 중심)

### 3. 요약 추출 규칙 — **Bridge가 자동 포맷팅 (Option C)**
- subgraph `is_done=True` 완료 시 bridge에서 아래 포맷의 `ToolMessage` 생성
```
[{subagent_name} 완료]
산출물: {artifact_path}
{last_ai_message[:200]}...
```
- subagent 페르소나를 건드리지 않고 parent context 격리 달성
- truncate 길이(200자)는 실사용 보며 튜닝

---

## 오픈 이슈 (Phase B2/B3 결정 시 재검토)

- **Consult 답변 주입**: 자동 vs User 승인 → 초안: User 승인
- **Meeting 참여자 approval**: 개별 vs 일괄(meeting 진입이 곧 승인) → 초안: 일괄
- **Cross-subagent 권한 제약**: 현재는 제약 없음 (모든 subagent가 서로 consult 가능)

---

## 진행 상태

- [x] Phase B1 착수 전 합의 3건 (확정)
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
- [ ] Task 4 (fallback 대비)
- [ ] Task 5
- [ ] Task 6
- [ ] Task 6.5 검증
- [ ] Phase B2 착수 결정
- [ ] Task 7
- [ ] Phase B3 착수 결정
- [ ] Task 8
- [ ] Phase B4 (memory, observability)
