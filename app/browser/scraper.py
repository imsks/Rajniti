"""Browser-use agent wrapper — real navigation + structured page extraction."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Generic, TypeVar

from browser_use import Agent
from pydantic import BaseModel

from app.browser.llm import build_browser_llm

T = TypeVar("T", bound=BaseModel)

LOCAL_LLM_SYSTEM_HINT = (
    "You control a real browser. Navigate the site, open pages, and read visible content. "
    "Never invent affidavit numbers — extract only what is on the page. "
    "Respond with raw JSON only — no markdown fences. "
    "The action field must be a JSON array. Call done only after reading the target page."
)

PLAIN_SCRAPE_SYSTEM_HINT = (
    "Respond with raw JSON only — no markdown code fences, no ```json blocks. "
    "Match the provided schema exactly. Do NOT include a thinking field. "
    "The action field must be a JSON array. Keep memory under 200 characters. "
    "Call done immediately once you have the answer."
)


@dataclass
class ScrapeResult:
    url: str
    task: str
    result: str
    steps_taken: int


@dataclass
class BrowserExtractResult(Generic[T]):
    url: str
    task: str
    data: T
    steps_taken: int


def _agent_settings() -> dict:
    return {
        "use_vision": os.getenv("AGENT_USE_VISION", "true").lower() in ("1", "true", "yes"),
        "llm_timeout": int(os.getenv("AGENT_LLM_TIMEOUT", "300")),
        "step_timeout": int(os.getenv("AGENT_STEP_TIMEOUT", "300")),
        "enable_planning": os.getenv("AGENT_ENABLE_PLANNING", "false").lower() in ("1", "true"),
        "flash_mode": os.getenv("AGENT_FLASH_MODE", "false").lower() in ("1", "true", "yes"),
        "use_thinking": os.getenv("AGENT_USE_THINKING", "false").lower() in ("1", "true"),
        "use_judge": os.getenv("AGENT_USE_JUDGE", "false").lower() in ("1", "true"),
        "max_actions_per_step": int(os.getenv("AGENT_MAX_ACTIONS_PER_STEP", "3")),
        "max_clickable_elements_length": int(os.getenv("AGENT_MAX_CLICKABLE_ELEMENTS_LENGTH", "8000")),
        "max_steps": int(os.getenv("AGENT_MAX_STEPS", "25")),
        "min_steps": int(os.getenv("AGENT_MIN_STEPS", "2")),
    }


def build_extract_task(url: str, instructions: str) -> str:
    return (
        f"Start at {url}. {instructions.strip()} "
        "Use browser actions (navigate, click, scroll) to reach the candidate profile. "
        "Read affidavit fields from the page, then submit structured output."
    )


def build_scrape_task(url: str, instructions: str | None = None) -> str:
    if instructions:
        return (
            f"Go to {url}. {instructions} "
            "Read the visible page text only — do not click unless necessary. "
            "When you have the answer, call done with a short plain-text result."
        )
    return (
        f"Go to {url}. "
        "Extract the page title, main headings, and key visible text. "
        "When finished, call done with a concise plain-text summary."
    )


async def run_extract_agent(
    url: str,
    instructions: str,
    *,
    output_model: type[T],
    max_steps: int | None = None,
) -> BrowserExtractResult[T]:
    settings = _agent_settings()
    task = build_extract_task(url, instructions)
    llm = build_browser_llm()
    extend = LOCAL_LLM_SYSTEM_HINT if os.getenv("USE_LOCAL_LLM", "").lower() in ("1", "true", "yes") else (
        "Navigate with the browser and extract only visible page content — do not guess."
    )

    agent = Agent(
        task=task,
        llm=llm,
        output_model_schema=output_model,
        directly_open_url=True,
        use_vision=settings["use_vision"],
        llm_timeout=settings["llm_timeout"],
        step_timeout=settings["step_timeout"],
        enable_planning=settings["enable_planning"],
        flash_mode=False,
        use_thinking=settings["use_thinking"],
        use_judge=settings["use_judge"],
        max_actions_per_step=settings["max_actions_per_step"],
        max_clickable_elements_length=settings["max_clickable_elements_length"],
        extend_system_message=extend,
    )

    steps = max_steps or settings["max_steps"]
    history = await agent.run(max_steps=steps)
    steps_taken = len(history)

    if steps_taken < settings["min_steps"]:
        raise RuntimeError(
            f"Browser agent took {steps_taken} step(s) — expected at least "
            f"{settings['min_steps']} (page may not have been visited)"
        )

    structured = history.get_structured_output(output_model) or history.structured_output
    if structured is None:
        snippet = (history.final_result() or "")[:500]
        raise ValueError(f"Browser agent returned no structured output: {snippet}")

    return BrowserExtractResult(
        url=url,
        task=task,
        data=structured,
        steps_taken=steps_taken,
    )


def run_browser_extract(
    url: str,
    instructions: str,
    *,
    output_model: type[T],
    max_steps: int | None = None,
) -> BrowserExtractResult[T]:
    """Sync entry: browser-use navigates, extracts page data into output_model."""
    return asyncio.run(
        run_extract_agent(url, instructions, output_model=output_model, max_steps=max_steps)
    )


async def run_scrape_agent_async(
    url: str,
    instructions: str | None = None,
    *,
    max_steps: int | None = None,
) -> ScrapeResult:
    settings = _agent_settings()
    task = build_scrape_task(url, instructions)
    llm = build_browser_llm()
    use_local = os.getenv("USE_LOCAL_LLM", "").lower() in ("1", "true", "yes")
    extend = PLAIN_SCRAPE_SYSTEM_HINT if use_local else (
        "Navigate with the browser and extract only visible page content — do not guess."
    )
    flash_mode = os.getenv("AGENT_FLASH_MODE", "true").lower() in ("1", "true", "yes")

    agent = Agent(
        task=task,
        llm=llm,
        use_vision=settings["use_vision"],
        llm_timeout=settings["llm_timeout"],
        step_timeout=settings["step_timeout"],
        enable_planning=settings["enable_planning"],
        flash_mode=flash_mode,
        use_thinking=settings["use_thinking"],
        use_judge=settings["use_judge"],
        max_actions_per_step=settings["max_actions_per_step"],
        max_clickable_elements_length=settings["max_clickable_elements_length"],
        extend_system_message=extend,
    )

    steps = max_steps or settings["max_steps"]
    history = await agent.run(max_steps=steps)
    final = history.final_result() or ""
    steps_taken = len(history)

    return ScrapeResult(
        url=url,
        task=task,
        result=final or "",
        steps_taken=steps_taken,
    )


def run_scrape_agent(
    url: str,
    instructions: str | None = None,
    *,
    max_steps: int | None = None,
) -> ScrapeResult:
    """Sync entry: plain-text browser scrape (locals-style)."""
    return asyncio.run(run_scrape_agent_async(url, instructions, max_steps=max_steps))
