"""Agents module — LangGraph agents run request-scoped.

Public facade. Import only from this package root, e.g.
`from app.agents import AgentsService, AgentTask, AgentResult`.
"""

from app.agents.dto import AgentResult, AgentTask
from app.agents.service import AgentsService

__all__ = ["AgentsService", "AgentTask", "AgentResult"]
