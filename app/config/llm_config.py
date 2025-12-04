"""
LLM Configuration Module

This module provides a clean, extendable configuration system for LLM providers.
It supports multiple providers (OpenAI, Perplexity) and can be easily extended
to support additional providers like Anthropic, Cohere, etc.
"""

import os
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    PERPLEXITY = "perplexity"


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""

    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Default model to use")
    temperature: float = Field(
        default=0.3, description="Temperature for response generation"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens in response"
    )


class LLMConfig(BaseModel):
    """
    Main LLM configuration class.

    This class manages configuration for all LLM providers.
    New providers can be added by:
    1. Adding a new enum value to LLMProvider
    2. Adding provider-specific configuration in the providers dict
    3. Implementing the provider in the LLM service
    """

    default_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI, description="Default LLM provider to use"
    )
    providers: Dict[LLMProvider, LLMProviderConfig] = Field(
        default_factory=dict, description="Configuration for each provider"
    )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Create configuration from environment variables.

        Environment variables:
        - LLM_PROVIDER: Default provider (openai/perplexity)
        - OPENAI_API_KEY: OpenAI API key
        - OPENAI_MODEL: OpenAI model (default: gpt-3.5-turbo)
        - PERPLEXITY_API_KEY: Perplexity API key
        - PERPLEXITY_MODEL: Perplexity model (default: sonar)

        Returns:
            LLMConfig instance
        """
        providers = {}

        # Configure OpenAI if API key is present
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            max_tokens = None
            if os.getenv("OPENAI_MAX_TOKENS"):
                try:
                    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS"))
                except (ValueError, TypeError):
                    pass  # Use None if invalid

            providers[LLMProvider.OPENAI] = LLMProviderConfig(
                api_key=openai_api_key,
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
                max_tokens=max_tokens,
            )

        # Configure Perplexity if API key is present
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_api_key:
            max_tokens = None
            if os.getenv("PERPLEXITY_MAX_TOKENS"):
                try:
                    max_tokens = int(os.getenv("PERPLEXITY_MAX_TOKENS"))
                except (ValueError, TypeError):
                    pass  # Use None if invalid

            providers[LLMProvider.PERPLEXITY] = LLMProviderConfig(
                api_key=perplexity_api_key,
                model=os.getenv("PERPLEXITY_MODEL", "sonar"),
                temperature=float(os.getenv("PERPLEXITY_TEMPERATURE", "0.3")),
                max_tokens=max_tokens,
            )

        # Determine default provider
        default_provider_str = os.getenv("LLM_PROVIDER", "openai").lower()
        try:
            default_provider = LLMProvider(default_provider_str)
        except ValueError:
            default_provider = LLMProvider.OPENAI

        return cls(default_provider=default_provider, providers=providers)

    def get_provider_config(
        self, provider: Optional[LLMProvider] = None
    ) -> LLMProviderConfig:
        """
        Get configuration for a specific provider.

        Args:
            provider: Provider to get config for. If None, uses default provider.

        Returns:
            LLMProviderConfig for the provider

        Raises:
            ValueError: If provider is not configured
        """
        provider = provider or self.default_provider

        if provider not in self.providers:
            raise ValueError(
                f"Provider {provider} not configured. "
                f"Available providers: {list(self.providers.keys())}"
            )

        return self.providers[provider]


# Global configuration instance
_llm_config: Optional[LLMConfig] = None


def get_llm_config() -> LLMConfig:
    """
    Get the global LLM configuration instance.

    This function implements a singleton pattern to ensure consistent
    configuration across the application.

    Returns:
        LLMConfig instance
    """
    global _llm_config

    if _llm_config is None:
        _llm_config = LLMConfig.from_env()

    return _llm_config
