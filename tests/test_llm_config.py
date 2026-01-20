"""
Integration tests for LLM Configuration and Service.

These tests verify that the Langchain-based LLM service
works correctly with the new configuration system.
"""

import os
import pytest
from unittest.mock import Mock, patch

# Set environment variables before importing
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["PERPLEXITY_API_KEY"] = "test-perplexity-key"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

from app.config.llm_config import (
    LLMConfig,
    LLMProvider,
    LLMProviderConfig,
    get_llm_config,
)
from app.services.llm_service import LLMService, get_llm_service


class TestLLMConfig:
    """Tests for LLM configuration."""

    def test_config_from_env(self):
        """Test that configuration is loaded from environment variables."""
        config = LLMConfig.from_env()

        assert config.default_provider == LLMProvider.OPENAI
        assert LLMProvider.OPENAI in config.providers
        assert LLMProvider.PERPLEXITY in config.providers

    def test_openai_config(self):
        """Test OpenAI provider configuration."""
        config = LLMConfig.from_env()
        openai_config = config.get_provider_config(LLMProvider.OPENAI)

        assert openai_config.api_key == "test-openai-key"
        assert openai_config.model == "gpt-3.5-turbo"
        assert openai_config.temperature == 0.3

    def test_perplexity_config(self):
        """Test Perplexity provider configuration."""
        config = LLMConfig.from_env()
        perplexity_config = config.get_provider_config(LLMProvider.PERPLEXITY)

        assert perplexity_config.api_key == "test-perplexity-key"
        assert perplexity_config.model == "sonar"
        assert perplexity_config.temperature == 0.3

    def test_get_provider_config_default(self):
        """Test getting config for default provider."""
        config = LLMConfig.from_env()
        default_config = config.get_provider_config()

        assert default_config.api_key == "test-openai-key"

    def test_get_provider_config_invalid(self):
        """Test that getting config for unconfigured provider raises error."""
        config = LLMConfig(
            default_provider=LLMProvider.OPENAI, providers={}
        )

        with pytest.raises(ValueError, match="not configured"):
            config.get_provider_config(LLMProvider.OPENAI)

    def test_singleton_config(self):
        """Test that get_llm_config returns the same instance."""
        config1 = get_llm_config()
        config2 = get_llm_config()

        assert config1 is config2


class TestLLMService:
    """Tests for LLM service."""

    @patch("app.services.llm_service.ChatOpenAI")
    def test_service_initialization_openai(self, mock_chat_openai):
        """Test that service initializes correctly with OpenAI."""
        service = LLMService(provider="openai")

        assert service.provider == LLMProvider.OPENAI
        assert service.provider_config.model == "gpt-3.5-turbo"
        mock_chat_openai.assert_called_once()

    @patch("app.services.llm_service.ChatOpenAI")
    def test_service_initialization_perplexity(self, mock_chat_openai):
        """Test that service initializes correctly with Perplexity."""
        service = LLMService(provider="perplexity")

        assert service.provider == LLMProvider.PERPLEXITY
        assert service.provider_config.model == "sonar"
        # Verify it's called with Perplexity's base URL
        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["base_url"] == "https://api.perplexity.ai"

    @patch("app.services.llm_service.ChatOpenAI")
    def test_service_initialization_default_provider(self, mock_chat_openai):
        """Test that service uses default provider when none specified."""
        service = LLMService()

        assert service.provider == LLMProvider.OPENAI

    @patch("app.services.llm_service.ChatOpenAI")
    def test_service_initialization_invalid_provider(self, mock_chat_openai):
        """Test that invalid provider falls back to default."""
        service = LLMService(provider="invalid-provider")

        assert service.provider == LLMProvider.OPENAI

    @patch("app.services.llm_service.ChatOpenAI")
    def test_get_llm_service_factory(self, mock_chat_openai):
        """Test the factory function."""
        service = get_llm_service(provider="openai")

        assert isinstance(service, LLMService)
        assert service.provider == LLMProvider.OPENAI

    @patch("app.services.llm_service.ChatOpenAI")
    def test_search_method(self, mock_chat_openai):
        """Test the search method."""
        # Setup mock
        mock_response = Mock()
        mock_response.content = "Test answer"
        mock_chat_model = Mock()
        mock_chat_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat_model

        service = LLMService(provider="openai")
        result = service.search("test query")

        assert result["query"] == "test query"
        assert result["answer"] == "Test answer"
        assert result["model"] == "gpt-3.5-turbo"
        assert "citations" in result
        assert "location" in result

    @patch("app.services.llm_service.ChatOpenAI")
    def test_search_with_location(self, mock_chat_openai):
        """Test search with location context."""
        mock_response = Mock()
        mock_response.content = "Test answer with location"
        mock_chat_model = Mock()
        mock_chat_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat_model

        service = LLMService(provider="openai")
        location = {"country": "IN", "region": "Delhi"}
        result = service.search("test query", location=location)

        assert result["query"] == "test query"
        assert result["location"] == location

        # Verify the query was enhanced with location
        call_args = mock_chat_model.invoke.call_args[0][0]
        messages_content = str(call_args)
        assert "Delhi" in messages_content

    @patch("app.services.llm_service.ChatOpenAI")
    def test_search_india(self, mock_chat_openai):
        """Test India-specific search."""
        mock_response = Mock()
        mock_response.content = "India search result"
        mock_chat_model = Mock()
        mock_chat_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat_model

        service = LLMService(provider="openai")
        result = service.search_india("test query", region="Delhi", city="New Delhi")

        assert result["location"]["country"] == "IN"
        assert result["location"]["region"] == "Delhi"
        assert result["location"]["city"] == "New Delhi"

    @patch("app.services.llm_service.ChatOpenAI")
    def test_search_error_handling(self, mock_chat_openai):
        """Test error handling in search method."""
        mock_chat_model = Mock()
        mock_chat_model.invoke.side_effect = Exception("API Error")
        mock_chat_openai.return_value = mock_chat_model

        service = LLMService(provider="openai")
        result = service.search("test query")

        assert "error" in result
        assert result["error"] == "API Error"
        assert result["answer"] is None

    @patch("app.services.llm_service.ChatOpenAI")
    def test_batch_search(self, mock_chat_openai):
        """Test batch search."""
        mock_response = Mock()
        mock_response.content = "Batch result"
        mock_chat_model = Mock()
        mock_chat_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat_model

        service = LLMService(provider="openai")
        queries = ["query 1", "query 2", "query 3"]
        results = service.batch_search(queries)

        assert len(results) == len(queries)
        # Verify combined query was created
        call_args = mock_chat_model.invoke.call_args[0][0]
        messages_content = str(call_args)
        assert "1. query 1" in messages_content
        assert "2. query 2" in messages_content
