"""Deterministic capability discovery and matching."""

from __future__ import annotations

import re

from .models import AgentProfile


def tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9_-]*", value.casefold()) if len(t) > 1}


def capability_score(agent: AgentProfile, query: str) -> float:
    wanted = tokens(query)
    if not wanted:
        return 0.0
    corpus = tokens(" ".join([agent.name, agent.description, *agent.capabilities]))
    return round(len(wanted & corpus) / len(wanted), 4)


def match_agents(agents: list[AgentProfile], query: str, limit: int = 20) -> list[tuple[AgentProfile, float]]:
    ranked = [(agent, capability_score(agent, query)) for agent in agents]
    ranked = [item for item in ranked if item[1] > 0]
    ranked.sort(key=lambda item: (-item[1], item[0].name.casefold()))
    return ranked[: max(1, min(limit, 100))]
