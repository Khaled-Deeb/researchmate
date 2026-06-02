import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Central project settings.

    The current project works in fallback mode without an API key.
    Later, OpenAI-powered mode will read the same settings.
    """

    mode: str = os.getenv("RESEARCHMATE_MODE", "fallback")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    @property
    def use_openai(self) -> bool:
        return self.mode.lower() == "openai" and bool(self.openai_api_key)


settings = Settings()