from langchain_ollama import ChatOllama

from src.config import MODEL_BASE_URL


def create_chat_model(model: str, temperature: float = 0.0) -> ChatOllama:
    return ChatOllama(
        model=model,
        base_url=MODEL_BASE_URL,
        temperature=temperature,
    )
