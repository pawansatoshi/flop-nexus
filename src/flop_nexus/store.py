"""SQLite persistence for the Nexus MVP."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import AgentProfile, ReputationVector, Task, TaskEvent


class Store:
    def __init__(self, path: str = "data/nexus.db") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    did TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id);
                """
            )

    def upsert_agent(self, agent: AgentProfile) -> AgentProfile:
        now = datetime.now(UTC).isoformat()
        with self._connect() as db:
            db.execute(
                """INSERT INTO agents(did,payload,created_at,updated_at)
                   VALUES(?,?,?,?)
                   ON CONFLICT(did) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
                (agent.did, agent.model_dump_json(), now, now),
            )
        return agent

    def get_agent(self, did: str) -> AgentProfile | None:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM agents WHERE did=?", (did,)).fetchone()
        return AgentProfile.model_validate_json(row["payload"]) if row else None

    def list_agents(self, capability: str | None = None) -> list[AgentProfile]:
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM agents ORDER BY updated_at DESC").fetchall()
        agents = [AgentProfile.model_validate_json(row["payload"]) for row in rows]
        if capability:
            wanted = capability.casefold()
            agents = [a for a in agents if any(wanted in c.casefold() for c in a.capabilities)]
        return agents

    def put_task(self, task: Task) -> Task:
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO tasks(id,payload,created_at,updated_at) VALUES(?,?,?,?)",
                (str(task.id), task.model_dump_json(), task.created_at.isoformat(), task.updated_at.isoformat()),
            )
        return task

    def get_task(self, task_id: str) -> Task | None:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM tasks WHERE id=?", (task_id,)).fetchone()
        return Task.model_validate_json(row["payload"]) if row else None

    def put_event(self, event: TaskEvent) -> TaskEvent:
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO events(event_id,task_id,payload,created_at) VALUES(?,?,?,?)",
                (event.event_id, str(event.task_id), event.model_dump_json(), event.created_at.isoformat()),
            )
        return event

    def events_for_task(self, task_id: str) -> list[TaskEvent]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT payload FROM events WHERE task_id=? ORDER BY created_at ASC", (task_id,)
            ).fetchall()
        return [TaskEvent.model_validate_json(row["payload"]) for row in rows]

    def reputation(self, did: str) -> ReputationVector:
        agent = self.get_agent(did)
        if agent is None:
            return ReputationVector(
                score=0,
                identity_verified=False,
                completed_tasks=0,
                completion_rate=0,
                unique_collaborators=0,
                response_reliability=0,
                evidence_count=0,
                self_interaction_penalty=0,
            )
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM events").fetchall()
        events: list[dict[str, Any]] = [json.loads(row["payload"]) for row in rows]
        mine = [e for e in events if e.get("actor_did") == did]
        completed = [e for e in mine if e.get("type") == "task.completed"]
        collaborators = {
            e.get("payload", {}).get("counterparty_did")
            for e in mine
            if e.get("payload", {}).get("counterparty_did") and e.get("payload", {}).get("counterparty_did") != did
        }
        requested = [e for e in mine if e.get("type") == "task.requested"]
        completion_rate = len(completed) / len(requested) if requested else 0.0
        self_events = [e for e in mine if e.get("payload", {}).get("counterparty_did") == did]
        penalty = min(1.0, len(self_events) / max(1, len(mine))) if mine else 0.0
        identity_verified = did.startswith("did:key:z")
        score = min(
            100.0,
            (20.0 if identity_verified else 0.0)
            + min(30.0, len(completed) * 2.0)
            + min(20.0, len(collaborators) * 2.0)
            + completion_rate * 20.0
            + min(10.0, len(mine) * 0.25)
            - penalty * 25.0,
        )
        return ReputationVector(
            score=round(max(0.0, score), 2),
            identity_verified=identity_verified,
            completed_tasks=len(completed),
            completion_rate=round(completion_rate, 4),
            unique_collaborators=len(collaborators),
            response_reliability=round(completion_rate, 4),
            evidence_count=len(mine),
            self_interaction_penalty=round(penalty, 4),
        )
