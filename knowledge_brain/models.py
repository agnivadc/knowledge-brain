from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["session", "human", "ingestion"]


def _new_id() -> str:
    return f"kn-{uuid.uuid4().hex[:12]}"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class KnowledgeNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    content: str
    tags: list[str]
    source_type: SourceType = "session"
    source_ref: str = ""
    created_at: str = Field(default_factory=_utc_now_iso)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class WriteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node: KnowledgeNode


class CompiledContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    items: list[KnowledgeNode]
    total_matches: int
    returned_count: int
    timestamp: str = Field(default_factory=_utc_now_iso)


class InputValidationError(ValueError):
    pass
