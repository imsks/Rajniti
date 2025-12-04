# LLM Configuration

This module provides a clean, extendable configuration system for Language Learning Model (LLM) providers.

## Overview

The configuration system is designed to be:
- **Simple**: Easy to understand and use
- **Extendable**: New providers can be added with minimal changes
- **Predictable**: Configuration is centralized and type-safe using Pydantic
- **Production-ready**: Uses environment variables for secure configuration

## Supported Providers

Currently supported LLM providers:
- **OpenAI**: ChatGPT models (gpt-3.5-turbo, gpt-4, etc.)
- **Perplexity**: Perplexity AI models (sonar, etc.)

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Default LLM provider (openai or perplexity)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=1000  # Optional

# Perplexity Configuration
PERPLEXITY_API_KEY=your-perplexity-api-key
PERPLEXITY_MODEL=sonar
PERPLEXITY_TEMPERATURE=0.3
PERPLEXITY_MAX_TOKENS=1000  # Optional
```

### Using the Configuration

```python
from app.config.llm_config import get_llm_config, LLMProvider

# Get the global configuration instance
config = get_llm_config()

# Access the default provider
print(config.default_provider)  # LLMProvider.OPENAI

# Get configuration for a specific provider
openai_config = config.get_provider_config(LLMProvider.OPENAI)
print(openai_config.model)  # gpt-3.5-turbo
print(openai_config.temperature)  # 0.3
```

## Using the LLM Service

The LLM service provides a unified interface for all providers using Langchain:

```python
from app.services.llm_service import get_llm_service

# Create a service using the default provider
service = get_llm_service()

# Or specify a provider explicitly
service = get_llm_service(provider="openai")
service = get_llm_service(provider="perplexity")

# Perform a search
result = service.search("What are the election results in Delhi?")
print(result["answer"])

# India-specific search
result = service.search_india(
    "Latest political news",
    region="Delhi",
    city="New Delhi"
)

# Batch search
results = service.batch_search([
    "Election results in Delhi",
    "Political parties in Maharashtra",
    "Latest news on Karnataka elections"
])
```

## Architecture

The configuration system consists of three main components:

### 1. Configuration Models (`llm_config.py`)

- **LLMProvider**: Enum of supported providers
- **LLMProviderConfig**: Configuration for a single provider
- **LLMConfig**: Main configuration class managing all providers

### 2. LLM Service (`llm_service.py`)

- **LLMService**: Unified service using Langchain abstractions
- **get_llm_service()**: Factory function to create service instances

### 3. Integration with Langchain

The service uses Langchain's chat model abstractions:
- `ChatOpenAI` for OpenAI
- `ChatOpenAI` with custom base_url for Perplexity (OpenAI-compatible API)

## Adding a New Provider

To add support for a new LLM provider (e.g., Anthropic, Cohere):

### 1. Update the LLMProvider enum

```python
# In app/config/llm_config.py
class LLMProvider(str, Enum):
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    ANTHROPIC = "anthropic"  # Add new provider
```

### 2. Add provider configuration in LLMConfig.from_env()

```python
# In app/config/llm_config.py, inside from_env() method
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_api_key:
    providers[LLMProvider.ANTHROPIC] = LLMProviderConfig(
        api_key=anthropic_api_key,
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet"),
        temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.3")),
        max_tokens=(
            int(os.getenv("ANTHROPIC_MAX_TOKENS"))
            if os.getenv("ANTHROPIC_MAX_TOKENS")
            else None
        ),
    )
```

### 3. Implement the provider in LLMService

```python
# In app/services/llm_service.py, inside _create_chat_model() method
from langchain_anthropic import ChatAnthropic

if self.provider == LLMProvider.ANTHROPIC:
    return ChatAnthropic(
        api_key=self.provider_config.api_key,
        model=self.provider_config.model,
        temperature=self.provider_config.temperature,
        max_tokens=self.provider_config.max_tokens,
    )
```

### 4. Install required dependencies

```bash
# Add to requirements.in
langchain-anthropic>=0.1.0
```

### 5. Update environment configuration

```bash
# Add to .env.example
# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet
ANTHROPIC_TEMPERATURE=0.3
```

That's it! The new provider is now available through the unified interface.

## Design Principles

This configuration system follows professional engineering practices:

1. **Separation of Concerns**: Configuration is separate from business logic
2. **Type Safety**: Using Pydantic models for validation
3. **DRY (Don't Repeat Yourself)**: Centralized configuration
4. **Single Responsibility**: Each class has one clear purpose
5. **Open/Closed Principle**: Open for extension (new providers), closed for modification
6. **Dependency Injection**: Services receive configuration, don't create it

## Migration from Old System

The old system used separate service files (`openai_service.py`, `perplexity_service.py`). 
The new system:
- Removes code duplication
- Uses Langchain for better abstraction
- Centralizes configuration
- Makes it easier to add new providers

Existing code using `get_llm_service()` continues to work without changes.
