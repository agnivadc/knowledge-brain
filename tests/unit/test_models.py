from __future__ import annotations

import json
import re
from datetime import datetime

import pytest
from pydantic import ValidationError

from knowledge_brain.models import (
    CompiledContextResponse,
    InputValidationError,
    KnowledgeNode,
    WriteResult,
)


def test_node_minimal_construction_uses_defaults():
    node = KnowledgeNode(content="hello", tags=["t1"])
    assert node.content == "hello"
    assert node.tags == ["t1"]
    assert node.source_type == "session"
    assert node.source_ref == ""
    assert node.confidence == 0.7


def test_default_id_format():
    node = KnowledgeNode(content="x", tags=["t"])
    assert re.fullmatch(r"kn-[0-9a-f]{12}", node.id)


def test_default_ids_are_unique():
    a = KnowledgeNode(content="x", tags=["t"])
    b = KnowledgeNode(content="x", tags=["t"])
    assert a.id != b.id


def test_default_created_at_is_iso_utc():
    node = KnowledgeNode(content="x", tags=["t"])
    parsed = datetime.fromisoformat(node.created_at)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_round_trip_node_via_json():
    node = KnowledgeNode(
        content="hello",
        tags=["t1", "t2"],
        source_type="human",
        source_ref="ref-1",
        confidence=0.9,
    )
    js = node.model_dump_json()
    restored = KnowledgeNode.model_validate_json(js)
    assert restored == node


def test_node_json_key_order_matches_declaration():
    node = KnowledgeNode(content="x", tags=["t"])
    obj = json.loads(node.model_dump_json())
    assert list(obj.keys()) == [
        "id",
        "content",
        "tags",
        "source_type",
        "source_ref",
        "created_at",
        "confidence",
    ]


@pytest.mark.parametrize("bad", [-0.1, 1.5, 2.0, -1.0])
def test_confidence_out_of_range_rejected(bad: float):
    with pytest.raises(ValidationError):
        KnowledgeNode(content="x", tags=["t"], confidence=bad)


def test_confidence_boundaries_accepted():
    KnowledgeNode(content="x", tags=["t"], confidence=0.0)
    KnowledgeNode(content="x", tags=["t"], confidence=1.0)


def test_invalid_source_type_rejected():
    with pytest.raises(ValidationError):
        KnowledgeNode(content="x", tags=["t"], source_type="bogus")


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        KnowledgeNode(content="x", tags=["t"], unknown_field=1)


def test_write_result_wraps_node():
    node = KnowledgeNode(content="x", tags=["t"])
    res = WriteResult(node=node)
    assert res.node == node
    restored = WriteResult.model_validate_json(res.model_dump_json())
    assert restored == res


def test_compiled_context_response_round_trip():
    n1 = KnowledgeNode(content="a", tags=["t"])
    n2 = KnowledgeNode(content="b", tags=["t"])
    resp = CompiledContextResponse(
        query="search",
        items=[n1, n2],
        total_matches=2,
        returned_count=2,
    )
    js = resp.model_dump_json()
    restored = CompiledContextResponse.model_validate_json(js)
    assert restored == resp


def test_compiled_context_response_default_timestamp_is_iso_utc():
    resp = CompiledContextResponse(query="q", items=[], total_matches=0, returned_count=0)
    parsed = datetime.fromisoformat(resp.timestamp)
    assert parsed.tzinfo is not None


def test_input_validation_error_is_value_error():
    assert issubclass(InputValidationError, ValueError)
    err = InputValidationError("nope")
    assert str(err) == "nope"
