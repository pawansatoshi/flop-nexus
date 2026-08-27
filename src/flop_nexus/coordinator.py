"""Task matching and lifecycle rules."""

from __future__ import annotations

from datetime import UTC

from .discovery import match_agents
from .models import AgentProfile, Task, TaskStatus

ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.REQUESTED: {TaskStatus.ACCEPTED, TaskStatus.CANCELLED},
    TaskStatus.ACCEPTED: {TaskStatus.PROCESSING, TaskStatus.CANCELLED},
    TaskStatus.PROCESSING: {TaskStatus.DELIVERED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.DELIVERED: {TaskStatus.VERIFIED, TaskStatus.FAILED},
    TaskStatus.VERIFIED: {TaskStatus.COMPLETED, TaskStatus.FAILED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
}


def transition(task: Task, target: TaskStatus) -> Task:
    if target not in ALLOWED_TRANSITIONS[task.status]:
        raise ValueError(f"invalid task transition: {task.status} -> {target}")
    task.status = target
    from datetime import datetime
    task.updated_at = datetime.now(UTC)
    return task


def select_provider(agents: list[AgentProfile], capability: str) -> AgentProfile | None:
    matches = match_agents(agents, capability, limit=1)
    return matches[0][0] if matches else None
