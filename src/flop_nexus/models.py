"""Domain models shared by the API and services."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class TaskStatus(StrEnum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentProfile(BaseModel):
    did: str = Field(min_length=20)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    capabilities: list[str] = Field(default_factory=list, max_length=100)
    endpoint: HttpUrl | None = None
    technocore_room: str | None = Field(default=None, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegistration(AgentProfile):
    proof: "SignedEvent | None" = None


class SignedEvent(BaseModel):
    did: str
    room: str = Field(min_length=1, max_length=200)
    nonce: int = Field(ge=0)
    signature: str
    text: str = Field(min_length=1, max_length=4096)
    seq: int | None = Field(default=None, ge=0)
    timestamp: datetime | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        return value.astimezone(timezone.utc)


class TaskCreate(BaseModel):
    requester_did: str
    capability: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=10000)
    provider_did: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Task(TaskCreate):
    id: UUID = Field(default_factory=uuid4)
    status: TaskStatus = TaskStatus.REQUESTED
    provider_did: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_event_ids: list[str] = Field(default_factory=list)


class ReputationVector(BaseModel):
    version: str = "2026-08-27"
    score: float = Field(ge=0, le=100)
    identity_verified: bool
    completed_tasks: int = Field(ge=0)
    completion_rate: float = Field(ge=0, le=1)
    unique_collaborators: int = Field(ge=0)
    response_reliability: float = Field(ge=0, le=1)
    evidence_count: int = Field(ge=0)
    self_interaction_penalty: float = Field(ge=0, le=1)


class TaskEvent(BaseModel):
    event_id: str
    task_id: UUID
    type: str
    actor_did: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signed_event: SignedEvent | None = None
