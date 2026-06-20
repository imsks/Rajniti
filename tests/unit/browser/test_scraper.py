"""Browser scraper task builder tests."""

from app.browser.scraper import build_extract_task


def test_build_extract_task_requires_navigation() -> None:
    task = build_extract_task("https://example.com", "Find the profile.")
    assert "https://example.com" in task
    assert "browser actions" in task.lower()
    assert "structured output" in task.lower()
