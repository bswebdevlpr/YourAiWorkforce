from langchain_ollama import ChatOllama

from src.config import MODEL_BASE_URL
from src.libs.metrics import LLMMetricsHandler


def create_chat_model(
    model: str,
    temperature: float = 0.0,
    num_ctx: int = 8192,
    role: str = "unknown",
    reasoning: bool | None = None,
) -> ChatOllama:
    """`role`은 계측 태그. 이 인스턴스의 모든 호출이 role/num_ctx/temperature와 함께
    metrics/llm_calls.jsonl 에 기록된다(LLM_METRICS=0으로 비활성).

    `reasoning=False`는 qwen3의 thinking 모드를 끈다. YES/NO 판정처럼 추론 과정이
    필요 없는 호출에서 생성-후-폐기되는 <think> 토큰(수백 개 = 수십 초)을 애초에
    만들지 않게 한다. 기본 None은 모델 기본값(thinking on) 유지 → 생성 호출은 그대로.
    """
    return ChatOllama(
        model=model,
        base_url=MODEL_BASE_URL,
        temperature=temperature,
        num_ctx=num_ctx,
        reasoning=reasoning,
        callbacks=[
            LLMMetricsHandler(
                role=role,
                model=model,
                temperature=temperature,
                num_ctx=num_ctx,
                reasoning=reasoning,
            )
        ],
    )
