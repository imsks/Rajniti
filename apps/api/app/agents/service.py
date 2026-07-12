"""Agents facade.

Runs agent tasks synchronously within the request that needs them
(request-scoped execution — see the repo plan). The `run` signature is designed
so a future always-on worker can consume the same `AgentTask` from an in-process
queue without changing callers.
"""

from __future__ import annotations

from app.agents.dto import AgentResult, AgentTask


class AgentsService:
    """Executes agent tasks."""

    def run(self, task: AgentTask) -> AgentResult:
        """Run a single agent task and return its result.

        Placeholder implementation. Real LangGraph orchestration is wired in
        during migration.
        """
        return AgentResult(
            task_kind=task.kind,
            answer=f"[stub] would run '{task.kind}' agent for: {task.prompt}",
            citations=[],
        )
