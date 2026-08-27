"""Evidence helpers for linking public events to tasks."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def evidence_digest(task_id: str, event_ids: list[str], dids: list[str]) -> str:
    payload = {"task_id": task_id, "event_ids": sorted(event_ids), "dids": sorted(set(dids))}
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(canonical).hexdigest()


def build_proof(task_id: str, event_ids: list[str], dids: list[str]) -> dict[str, Any]:
    return {
        "schema": "flop-nexus/task-proof/v1",
        "task_id": task_id,
        "event_ids": sorted(event_ids),
        "dids": sorted(set(dids)),
        "digest": evidence_digest(task_id, event_ids, dids),
    }
