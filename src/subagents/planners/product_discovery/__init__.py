from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.path import PRD_PATH
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.libs.subgraph import build_conversational_subgraph
from src.subagents.planners.product_discovery.tools import save_prd


def build_product_discovery(checkpointer=None):
    return build_conversational_subgraph(
        persona=load_persona(PRODUCT_DISCOVERY),
        # 페르소나 ~10.5k 토큰 + 대화 누적 여유 → 20k. PRD 템플릿/Step 가이드가 후반부에 위치해 잘림 방지.
        model=create_chat_model(
            MODEL_NAME_PLANNER, temperature=0.5, num_ctx=20480,
            role="planner:product_discovery:gen",
        ),
        # check_done YES/NO 판정은 결정성이 우선. 동일 모델 파일(qwen3:8b) 이지만 temp=0 별도 인스턴스.
        # NOTE: MODEL_NAME_CRITIC(deepseek-r1:8b)는 reasoning 모델 특성상 binary 지시를 무시하고
        # 대화형으로 응답하는 문제 있음 (검증 결과). 추후 prompt 보강 또는 structured output 도입 시 재검토.
        critic_model=create_chat_model(
            MODEL_NAME_PLANNER, temperature=0.0, num_ctx=4096,
            role="critic:product_discovery:done",
            # YES/NO 판정엔 추론 과정이 불필요. thinking을 끄면 생성-후-폐기 토큰
            # (~500개 = ~25초)이 사라지고 판정이 즉시 나온다. → docs/metrics 참고.
            reasoning=False,
        ),
        save_tool=save_prd,
        artifact_path=PRD_PATH,
        checkpointer=checkpointer,
    )
