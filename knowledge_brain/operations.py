from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import CompiledContextResponse, KnowledgeNode, SourceType, WriteResult
from .quality import validate_query_input, validate_write_input


class BrainStore(Protocol):
    def write_node(self, node: KnowledgeNode) -> None: ...

    def query(
        self,
        query_text: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> tuple[list[KnowledgeNode], int]: ...

    def all_nodes(self) -> list[KnowledgeNode]: ...


class BrainOperations:
    def __init__(self, store: BrainStore):
        self.store = store

    @classmethod
    def from_db(cls, db_path: str | Path) -> "BrainOperations":
        from .store import Store
        return cls(Store(Path(db_path)))

    def write(
        self,
        *,
        content: str,
        tags: list[str],
        source_type: SourceType = "session",
        source_ref: str = "",
        confidence: float = 0.7,
        max_input_tokens: int = 2000,
    ) -> WriteResult:
        validate_write_input(content, tags, max_input_tokens)
        node = KnowledgeNode(
            content=content,
            tags=tags,
            source_type=source_type,
            source_ref=source_ref,
            confidence=confidence,
        )
        self.store.write_node(node)
        return WriteResult(node=node)

    def query(
        self,
        *,
        query: str,
        tags: list[str] | None = None,
        max_input_tokens: int = 500,
        max_results: int = 10,
    ) -> CompiledContextResponse:
        validate_query_input(query, max_input_tokens)
        items, total = self.store.query(query_text=query, tags=tags, limit=max_results)
        return CompiledContextResponse(
            query=query,
            items=items,
            total_matches=total,
            returned_count=len(items),
        )

    def export(self) -> list[KnowledgeNode]:
        return self.store.all_nodes()
