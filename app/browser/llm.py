"""Browser-use LLM — same credentials as agent_config (USE_LOCAL_LLM)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, TypeVar, overload

import httpx
from browser_use import ChatOpenAI
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion
from pydantic import BaseModel

from app.browser.parsing import parse_structured_agent_json
from app.config.agent_config import llm_openai_kwargs, use_local_llm

T = TypeVar("T", bound=BaseModel)


def wrap_output_format(output_format: type[T]) -> type[T]:
    class NormalizedOutputFormat(output_format):
        @classmethod
        def model_validate_json(
            cls,
            json_data: str | bytes | bytearray,
            *,
            strict: bool | None = None,
        ) -> T:
            text = (
                json_data.decode()
                if isinstance(json_data, (bytes, bytearray))
                else str(json_data)
            )
            return super().model_validate_json(
                parse_structured_agent_json(text), strict=strict
            )

    NormalizedOutputFormat.__name__ = output_format.__name__
    NormalizedOutputFormat.__qualname__ = output_format.__qualname__
    return NormalizedOutputFormat


@dataclass
class LocalBrowserChatOpenAI(ChatOpenAI):
    """LM Studio often returns malformed JSON — normalize before validation."""

    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: None = None, **kwargs: Any
    ) -> ChatInvokeCompletion[str]: ...

    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T], **kwargs: Any
    ) -> ChatInvokeCompletion[T]: ...

    async def ainvoke(
        self,
        messages: list[BaseMessage],
        output_format: type[T] | None = None,
        **kwargs: Any,
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        if output_format is not None:
            output_format = wrap_output_format(output_format)
        return await super().ainvoke(messages, output_format=output_format, **kwargs)


def build_browser_llm() -> ChatOpenAI:
    kw = llm_openai_kwargs()
    timeout = httpx.Timeout(
        float(os.getenv("LMSTUDIO_REQUEST_TIMEOUT", "300") if use_local_llm() else os.getenv("FREE_TIER_LLM_TIMEOUT_SECS", "120")),
        connect=30.0,
    )

    if use_local_llm():
        return LocalBrowserChatOpenAI(
            **kw,
            timeout=timeout,
            max_completion_tokens=int(os.getenv("LMSTUDIO_MAX_COMPLETION_TOKENS", "4096")),
            add_schema_to_system_prompt=True,
            dont_force_structured_output=True,
            remove_min_items_from_schema=True,
            remove_defaults_from_schema=True,
        )

    return ChatOpenAI(**kw, timeout=timeout)
