# 서브에이전트 독립 thread + 브리핑 기반 컨텍스트 전파 리팩토링 계획

## 배경 및 목표

현재: parent 그래프의 단일 AsyncSqliteSaver가 서브그래프에도 전파 → 모든 대화가 parent thread 하나에 누적. 서브에이전트 간 state 공유로 역할 경계 흐려짐, 토큰 낭비. 게다가 LangGraph 1.1.2 Studio에서 subgraph resume이 task ID 해시 불일치로 무음 실패하는 버그 관측됨.

**Phase B1 목표 (이번 착수 범위)**:
1. **서브에이전트 messages 격리** (state schema 분리) ← 핵심
2. Orchestrator만 전체 맥락 보관, 서브에이전트에는 **브리핑 패킷만** 전달
3. 중복 주입 / cross-talk 문제 해소

**Phase B2/B3 목표 (이연)**:
- 독립 thread_id + 재진입 시 과거 대화 자동 복원 → Phase B2에서 재평가
- Cross-subagent consultation (방식 A) → Phase B2
- Meeting mode (방식 B) → Phase B3 (수요 확인 후)

> **Option A (외부 ainvoke + 수동 interrupt passthrough) → Option B (state schema 분리)로 전환**
> 이유: LangGraph 1.1.2 subgraph resume 버그 확인 직후, 수동 passthrough도 같은 저수준에 의존. Option B는 LangGraph의 기본 interrupt 전파 경로를 유지하면서 핵심 요구(messages 격리)를 달성.

---

## 설계 결정 (확정 — Option B)

| 쟁점 | 결정 | 근거 |
|---|---|---|
| 1. 체크포인터 분리 | **Phase B1에선 단일 thread 유지** | Option B는 parent와 subgraph가 같은 thread, `checkpoint_ns`로 네임스페이스만 분리. 독립 thread는 Phase B2로 이연 |
| 2. 서브그래프 호출 구조 | **subgraph를 parent 노드로 유지 + state schema 분리** | `SubagentState` 별도 TypedDict 정의. LangGraph input/output transformer로 parent↔subgraph 데이터 변환 |
| 3. 브리핑 생성 방식 | **템플릿 기반** | tool schema 확장으로 orchestrator LLM이 직접 구성 (`query`/`context_hints`/`artifact_refs`) |
| 4. Interrupt 라우팅 | **LangGraph 자동 전파 활용** | subgraph interrupt → parent로 자동 올라옴. 수동 passthrough 불필요 |
| 5. 재진입 thread 복원 | **Phase B1에선 근사 복원** | parent messages 중 해당 subagent 구간을 transformer가 subgraph input으로 되살림. 완전 복원은 Phase B2에서 독립 thread 도입과 함께 |
| 6. 반환값 병합 | **요약 ToolMessage만 parent로** | subgraph output transformer에서 last AIMessage 요약만 parent messages에 기록. 중간 대화는 subgraph namespace에만 체류 |

---

## Phase 분할 (스코프 재조정)

### Phase B1 — MVP (이번 착수, Option B)
State schema 분리 + 브리핑 템플릿. LangGraph 기본 interrupt 전파 활용. 핵심 요구인 "messages 격리 / 중복 주입 해소"를 안전하게 달성.

### Phase B2 — 독립 thread + 방식 A (consult)
Phase B1 운영 확인 후:
- LangGraph 버전 업데이트(1.2+) 시 subgraph resume 안정성 재평가
- 독립 thread_id 도입 (재진입 시 자동 복원)
- `consult_subagent` tool로 서브에이전트 간 단발 Q&A 중계

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

#### Task 4: State schema 분리 + transformer 구현 — 핵심 `[L3 / opus, 메인 직접]`
- **파일**: 신규 `src/subagents/state.py`, `src/libs/subgraph.py` 수정, `src/agent.py` (bridge 재작성)
- **설계 방향**: subgraph를 parent 노드로 유지하되 state schema를 완전히 분리. bridge 노드가 parent state → subgraph input 변환 + subgraph output → parent 병합을 모두 담당.

**세부 작업**:
1. **`SubagentState` TypedDict 신규 정의** (`src/subagents/state.py` 또는 `src/libs/subgraph.py`)
   ```python
   class SubagentState(TypedDict, total=False):
       messages: Annotated[list, add_messages]
       is_done: bool
   ```
   - parent의 `_last_subgraph`, `_approved_subagents`, `_subagent_threads` 등은 **포함 안 함** → subagent가 볼 수 없음

2. **`build_conversational_subgraph` 수정**: `StateGraph(SubagentState)`로 변경. 내부 call_model/wait_for_user/check_done 등 노드가 `SubagentState`만 다루도록 타입 조정.

3. **bridge 노드 재작성** (`src/agent.py`):
   - **input transform**: tool_call args에서 `query`/`context_hints`/`artifact_refs` 추출 → 3섹션 브리핑 HumanMessage 구성
   - **subgraph 호출**: `subgraph.invoke({"messages": [brief_msg]}, config)` — parent config 상속, LangGraph가 `checkpoint_ns`로 subgraph 상태를 자동 분리. interrupt는 LangGraph가 parent로 자동 전파
   - **output transform**: subgraph 결과의 last AIMessage에서 요약 추출 → `ToolMessage(tool_call_id=..., content="[{name} 완료]\n산출물: {path}\n{text[:200]}...")`로 parent messages에 추가
   - `goto="review"` 로 parent 다음 노드 지정

4. **기존 `add_node(name, spec.graph_factory(None))` 제거**: subagent는 bridge가 내부 invoke만 하므로 parent의 별도 노드로 둘 필요 없음. 단, LangGraph 패턴에 따라 compiled subgraph는 bridge 내부에서 참조 가능하도록 module-level 또는 closure로 보관

5. **에러 처리**: subgraph invoke 중 예외 시 `ToolMessage(content=f"[{name} 실행 실패] {exc}")` 로 parent에 기록하고 orchestrator로 복귀

- **Option B 이점**: LangGraph 1.1.2의 기본 interrupt 전파 경로를 그대로 사용 → 수동 passthrough 불필요, Studio resume 버그와 무관한 영역
- **선행**: Task 1, Task 2, Task 3 (모두 완료)

#### Task 5: Parent 그래프 배선 정리 `[L2 / sonnet]`
- **파일**: `src/agent.py`
- **내용**:
  - `graph()` / `_build()` 에서 `for name, spec in SUBAGENT_REGISTRY.items(): builder.add_node(name, spec.graph_factory(None))` 제거 (Task 4에서 이미 했으면 skip)
  - `builder.add_edge(name, "review")` 루프 제거 → bridge가 완료 시 직접 review로 goto
  - conditional_edges 단순화: orchestrator → bridge (subagent 이름별 매핑이 아니라 단일 bridge 노드로)
  - approval_gate는 유지 (reset_project 게이트용)
- **선행**: Task 4

#### Task 6: main.py / 전체 검증 `[L2 / sonnet]`
- **파일**: `src/main.py` (영향 적음), 필요 시 간단 TestClient 스크립트
- **내용**:
  - Option B는 parent thread 하나에 모든 resume이 집중됨 → `main.py`의 기존 resume 로직 그대로 동작 예상. 변경 최소
  - TestClient 시나리오 2~3개로 end-to-end 동작 확인
    - product_discovery 호출 → interrupt → reply → 완료
    - subagent messages가 parent에 full text로 섞이지 않고 요약만 병합되는지 확인
    - reset_project 이후 동작
- **선행**: Task 5

#### 🔍 Task 6.5: E2E 검증 체크포인트
- **내용**: Task 6 이후 다음 시나리오 수동 검증 후 커밋 고정
  - 서브에이전트 첫 호출 → interrupt → resume → 완료
  - 완료 후 parent messages에 요약 ToolMessage만 들어있고 subagent 중간 대화는 안 섞여있는지 LangSmith 트레이스로 확인
  - Orchestrator가 동일 subagent 재호출 시 parent의 요약만 보이는지
  - reset_project 이후 clean 상태에서 처음부터 동작
  - 중복 HumanMessage 주입 사라졌는지 (Option A 원래 목적 중 하나)
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

## 리스크 및 대응 (Option B 기준)

| 리스크 | 영향 | 대응 |
|---|---|---|
| **LangGraph state schema 전환 시 타입 에러** | Task 4 blocker | SubagentState를 최소 필드로 시작, invoke 경로 먼저 동작 확인 후 확장 |
| **input/output transformer 누락으로 parent messages 오염** | 중간 대화가 parent로 새어나감 | Task 4에서 bridge의 output transform을 명시적으로 last AIMessage 요약만 추출 |
| **Memory 누적 → context 초과** | 장기 | Phase B4 압축 전략 |
| **재진입 시 과거 대화 복원 미흡** | UX 저하 | Phase B1에선 브리핑 의존, Phase B2 독립 thread로 해결 |
| **subagent invoke 실패 처리 미정의** | 런타임 에러 | Task 4에 try/except + ToolMessage("[실행 실패] ...") 반환 로직 포함 |

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
- [x] **Option A → Option B 전환 결정** (state schema 분리 방식 채택)
- [x] Task 1 (State 필드 추가) — 커밋 669ea2b
- [x] Task 2 (Tool schema 확장) — 커밋 fb32808
- [x] Task 3 (Subgraph factory) — 커밋 9a20cfa
- [ ] Task 4 (State schema 분리 + transformer)
- [ ] Task 5 (배선 정리)
- [ ] Task 6 (main.py 검증)
- [ ] Task 6.5 E2E 검증
- [ ] Phase B2 착수 결정 (독립 thread + consult)
- [ ] Task 7 (consult)
- [ ] Phase B3 착수 결정 (meeting)
- [ ] Task 8 (meeting)
- [ ] Phase B4 (memory, observability)

### Task 1~3 유산 취급 (Option B 하에서)
- `_subagent_threads`, `_active_subagent`, `_active_subagent_thread` 필드 — **Phase B2 대비로 예약**. Phase B1에선 미사용
- `context_hints`, `artifact_refs` tool schema 확장 — **즉시 사용** (Task 4 브리핑 템플릿 구성 시)
- `graph_factory` 패턴 — **즉시 사용** (Task 4에서 bridge가 내부 invoke할 때 factory로 compile)
