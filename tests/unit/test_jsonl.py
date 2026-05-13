from __future__ import annotations

import json

import pytest

from knowledge_brain.jsonl import (
    JsonlNodeDecodeError,
    decode_node,
    encode_node,
    encode_nodes,
    format_import_summary,
    import_nodes_from_lines,
)
from knowledge_brain.models import KnowledgeNode


class FakeMergeStore:
    def __init__(self, results: list[str]):
        self.results = results
        self.merged: list[tuple[KnowledgeNode, bool]] = []

    def merge_node(self, node: KnowledgeNode, *, force: bool = False):
        self.merged.append((node, force))
        return self.results.pop(0)


def test_encode_node_uses_sorted_json_keys():
    node = KnowledgeNode(
        id="kn-1",
        content="hello",
        tags=["t"],
        source_type="human",
        source_ref="ref",
        created_at="2026-01-01T00:00:00+00:00",
        confidence=0.8,
    )

    assert encode_node(node) == (
        '{"confidence": 0.8, "content": "hello", '
        '"created_at": "2026-01-01T00:00:00+00:00", "id": "kn-1", '
        '"source_ref": "ref", "source_type": "human", "tags": ["t"]}'
    )


def test_encode_nodes_preserves_input_order():
    first = KnowledgeNode(id="kn-a", content="a", tags=["t"])
    second = KnowledgeNode(id="kn-b", content="b", tags=["t"])

    assert encode_nodes([first, second]) == [encode_node(first), encode_node(second)]


def test_decode_node_reports_line_number_for_malformed_json():
    with pytest.raises(JsonlNodeDecodeError, match="line 7"):
        decode_node("not json", line_no=7)


def test_import_nodes_from_lines_ignores_blank_lines_and_counts_merge_results():
    first = KnowledgeNode(id="kn-a", content="a", tags=["t"])
    second = KnowledgeNode(id="kn-b", content="b", tags=["t"])
    store = FakeMergeStore(["inserted", "skipped"])

    summary = import_nodes_from_lines(
        ["\n", encode_node(first), "  \n", encode_node(second)],
        store,
    )

    assert summary.inserted == 1
    assert summary.skipped == 1
    assert summary.replaced == 0
    assert [node.id for node, _ in store.merged] == ["kn-a", "kn-b"]


def test_import_nodes_from_lines_passes_force_to_merge():
    node = KnowledgeNode(id="kn-a", content="a", tags=["t"])
    store = FakeMergeStore(["replaced"])

    summary = import_nodes_from_lines([json.dumps(node.model_dump(mode="json"))], store, force=True)

    assert summary.replaced == 1
    assert store.merged == [(node, True)]


def test_import_nodes_from_lines_stops_on_bad_line():
    node = KnowledgeNode(id="kn-a", content="a", tags=["t"])
    store = FakeMergeStore(["inserted"])

    with pytest.raises(JsonlNodeDecodeError, match="line 2"):
        import_nodes_from_lines([encode_node(node), "bad"], store)

    assert [merged.id for merged, _ in store.merged] == ["kn-a"]


def test_format_import_summary():
    node = KnowledgeNode(id="kn-a", content="a", tags=["t"])
    store = FakeMergeStore(["inserted"])
    summary = import_nodes_from_lines([encode_node(node)], store)

    assert format_import_summary(summary) == "import complete: 1 inserted, 0 skipped, 0 replaced"
