from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import settings


def require_openai_config() -> None:
    """
    Ensure OpenAI mode is enabled and an API key is available.

    This prevents accidental API calls when the project is running
    in fallback mode.
    """
    if not settings.use_openai:
        raise RuntimeError(
            "OpenAI mode is not enabled. "
            "Set RESEARCHMATE_MODE=openai and OPENAI_API_KEY in .env."
        )


def get_chat_model() -> ChatOpenAI:
    """
    Create the OpenAI chat model.

    This function should only be called by future OpenAI-powered features.
    """
    require_openai_config()

    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
    )


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Create the OpenAI embedding model.

    This function should only be called by future semantic search features.
    """
    require_openai_config()

    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
    )