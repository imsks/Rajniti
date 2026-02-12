import os
import logging
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

PROVIDER_CONFIGS = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "AGENT_OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "base_url": None,
    },
    "perplexity": {
        "api_key_env": "PERPLEXITY_API_KEY",
        "model_env": "AGENT_PERPLEXITY_MODEL",
        "default_model": "sonar",
        "base_url": "https://api.perplexity.ai",
    },
}


def _build_llm(provider: str) -> Optional[ChatOpenAI]:
    cfg = PROVIDER_CONFIGS.get(provider)
    if not cfg:
        return None

    api_key = os.getenv(cfg["api_key_env"])
    if not api_key:
        return None

    model = os.getenv(cfg["model_env"], cfg["default_model"])

    kwargs = dict(api_key=api_key, model=model, temperature=0)
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]

    return ChatOpenAI(**kwargs)


def get_agent_llm() -> ChatOpenAI:
    fallback_str = os.getenv("AGENT_LLM_PROVIDERS", "perplexity,openai")
    providers = [p.strip() for p in fallback_str.split(",") if p.strip()]

    for provider in providers:
        llm = _build_llm(provider)
        if llm is None:
            logger.warning("Agent LLM: %s skipped (no API key)", provider)
            continue
        logger.info("Agent LLM: using %s (%s)", provider, llm.model_name)
        return llm

    raise RuntimeError(
        f"No working LLM provider found. Tried: {providers}. "
        "Check your API keys in .env"
    )
