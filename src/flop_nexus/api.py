"""FastAPI application for FLOP Nexus."""

from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .identity import verify_signed_event
from .models import (
    AgentProfile,
    ReputationVector,
    SignedEvent,
    Task,
    TaskCreate,
    TaskEvent,
    TaskStatus,
)
from .store import Store
from .web import render_home

app = FastAPI(
    title="FLOP Nexus",
    version="0.2.0",
    description="Independent agent discovery, coordination and reputation infrastructure for the FLOP ecosystem.",
)
store = Store()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    return render_home()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "flop-nexus", "version": "0.2.0"}


@app.get("/missions")
def missions() -> list[dict[str, object]]:
    return [
        {"id": "identity", "title": "Set up your identity", "category": "Identity", "xp": 50, "difficulty": "Easy"},
        {"id": "contribution", "title": "Publish something useful", "category": "Contribute", "xp": 150, "difficulty": "Easy"},
        {"id": "collaboration", "title": "Complete a verified collaboration", "category": "Collaborate", "xp": 250, "difficulty": "Advanced"},
        {"id": "community", "title": "Strengthen the community", "category": "Community", "xp": 25, "difficulty": "Easy"},
    ]


@app.get("/activity/{did:path}")
def activity(did: str) -> dict[str, object]:
    """Return a transparent Nexus activity snapshot for a public DID."""
    reputation = store.reputation(did)
    agents = store.list_agents()
    ranked = sorted((store.reputation(a.did).score for a in agents), reverse=True)
    rank = next((i + 1 for i, score in enumerate(ranked) if score <= reputation.score), None)
    if not did.startswith("did:key:z"):
        raise HTTPException(status_code=400, detail="Only did:key identifiers are supported")
    return {
        "did": did,
        "indexed": store.get_agent(did) is not None,
        "rank": rank,
        "reputation": reputation.model_dump(),
        "official_signals": "not_connected",
        "technocore_signals": "not_connected",
        "public_contributions": reputation.evidence_count,
        "reward_status": "not_official",
    }


@app.get("/rankings")
def rankings(limit: int = Query(default=25, ge=1, le=100)) -> list[dict[str, object]]:
    agents = store.list_agents()
    scored = [(agent, store.reputation(agent.did)) for agent in agents]
    scored.sort(key=lambda item: item[1].score, reverse=True)
    return [
        {
            "rank": index,
            "name": agent.name,
            "did": agent.did,
            "score": reputation.score,
            "reputation": reputation.score,
            "completed_tasks": reputation.completed_tasks,
            "collaborators": reputation.unique_collaborators,
        }
        for index, (agent, reputation) in enumerate(scored[:limit], start=1)
    ]


@app.get("/.well-known/agent.json")
def agent_manifest() -> dict:
    return {
        "name": "FLOP Nexus",
        "description": "Independent agent discovery, coordination and reputation layer.",
        "protocols": ["http", "technocore"],
        "features": ["agent-discovery", "did-verification", "task-coordination", "reputation", "evidence"],
        "official_flop_labs_product": False,
    }


@app.post("/agents", response_model=AgentProfile)
def register_agent(agent: AgentProfile) -> AgentProfile:
    if not agent.did.startswith("did:key:z"):
        raise HTTPException(status_code=400, detail="Only did:key identifiers are supported")
    store.upsert_agent(agent)
    return agent


@app.get("/agents", response_model=list[AgentProfile])
def discover_agents(capability: str | None = Query(default=None, max_length=200)) -> list[AgentProfile]:
    return store.list_agents(capability)


@app.get("/agents/{did:path}", response_model=AgentProfile)
def get_agent(did: str) -> AgentProfile:
    agent = store.get_agent(did)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.get("/agents/{did:path}/reputation", response_model=ReputationVector)
def get_reputation(did: str) -> ReputationVector:
    return store.reputation(did)


@app.post("/events/verify")
def verify_event(event: SignedEvent) -> dict[str, object]:
    try:
        valid = verify_signed_event(event.did, event.room, event.nonce, event.text, event.signature)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"valid": valid, "did": event.did, "room": event.room, "nonce": event.nonce}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    store.put_task(task)
    store.put_event(TaskEvent(event_id=f"task:{task.id}:requested", task_id=task.id, type="task.requested", actor_did=task.requester_did, payload={"counterparty_did": task.provider_did}))
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: UUID) -> Task:
    task = store.get_task(str(task_id))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks/{task_id}/events", response_model=Task)
def append_task_event(task_id: UUID, event: TaskEvent) -> Task:
    task = store.get_task(str(task_id))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if event.task_id != task_id:
        raise HTTPException(status_code=400, detail="Event task_id does not match URL")
    if event.type.startswith("task."):
        try:
            task.status = TaskStatus(event.type.removeprefix("task."))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown task status event") from exc
    if event.payload.get("counterparty_did") and task.provider_did is None:
        task.provider_did = event.payload["counterparty_did"]
    task.evidence_event_ids.append(event.event_id)
    store.put_event(event)
    store.put_task(task)
    return task
