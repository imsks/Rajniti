"""DTOs crossing the agents boundary."""

from __future__ import annotations

from pydantic import BaseModel


class AgentTask(BaseModel):
    """A unit of work handed to an agent.

    Kept intentionally simple. Because execution is request-scoped today, this
    doubles as the interface a future always-on background worker would consume
    from an in-process queue.
    """

    kind: str
    prompt: str
    context: dict[str, str] = {}


class AgentResult(BaseModel):
    """The output of running an :class:`AgentTask`."""

    task_kind: str
    answer: str
    citations: list[str] = []
