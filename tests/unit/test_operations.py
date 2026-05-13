from __future__ import annotations

import pytest

from knowledge_brain.models import InputValidationError, KnowledgeNode, WriteResult
from knowledge_brain.operations import BrainOperations


class FakeStore:
    def __init__(self):
        self.written: list[KnowledgeNode] = []
        self.query_args: tuple[str | None, list[str] | None, int] | None = None
        self.query_items = [
            KnowledgeNode(content="alpha story", tags=["story", "a"]),
        ]
        self.query_total = 3
        self.export_nodes = [
            KnowledgeNode(content="exported", tags=["backup"]),
        ]

    def write_node(self, node: KnowledgeNode) -> None:
        self.written.append(node)

    def query(
        self,
        query_text: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> tuple[list[KnowledgeNode], int]:
        self.query_args = (query_text, tags, limit)
        return self.query_items, self.query_total

    def all_nodes(self) -> list[KnowledgeNode]:
        return self.export_nodes


def test_write_validates_constructs_and_persists_node():
    store = FakeStore()

    result = BrainOperations(store).write(
        content="hello brain",
        tags=["mvp"],
        source_type="human",
        source_ref="note-1",
        confidence=0.8,
    )

    assert isinstance(result, WriteResult)
    assert store.written == [result.node]
    assert result.node.content == "hello brain"
    assert result.node.tags == ["mvp"]
    assert result.node.source_type == "human"
    assert result.node.source_ref == "note-1"
    assert result.node.confidence == 0.8


def test_write_rejects_invalid_input_before_persisting():
    store = FakeStore()

    with pytest.raises(InputValidationError, match="content must not be empty"):
        BrainOperations(store).write(content=" ", tags=["mvp"])

    assert store.written == []


def test_query_validates_delegates_and_wraps_response():
    store = FakeStore()

    response = BrainOperations(store).query(
        query="alpha",
        tags=["story"],
        max_results=5,
    )

    assert store.query_args == ("alpha", ["story"], 5)
    assert response.query == "alpha"
    assert response.items == store.query_items
    assert response.total_matches == 3
    assert response.returned_count == 1


def test_query_rejects_invalid_input_before_store_call():
    store = FakeStore()

    with pytest.raises(InputValidationError, match="query must not be empty"):
        BrainOperations(store).query(query=" ")

    assert store.query_args is None


def test_export_returns_all_nodes_from_store():
    store = FakeStore()

    assert BrainOperations(store).export() == store.export_nodes
