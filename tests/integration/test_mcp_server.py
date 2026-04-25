from __future__ import annotations

from pathlib import Path

import pytest

from knowledge_brain.mcp import server as srv
from knowledge_brain.models import CompiledContextResponse, InputValidationError, WriteResult
from knowledge_brain.store import Store


@pytest.fixture(autouse=True)
def _isolate_db(tmp_path: Path, monkeypatch):
    db = tmp_path / "knowledge.db"
    monkeypatch.setenv("BRAIN_DB_PATH", str(db))
    Store(db).init_schema()
    return db


async def test_server_registers_brain_tools():
    tool_names = {t.name for t in await srv.mcp.list_tools()}
    assert "brain_write" in tool_names
    assert "brain_query" in tool_names


async def test_brain_write_persists_and_returns_result():
    result = await srv.brain_write(
        content="hello brain",
        tags=["mvp"],
    )
    assert isinstance(result, WriteResult)
    assert result.node.content == "hello brain"
    assert result.node.source_type == "session"
    assert result.node.tags == ["mvp"]


async def test_brain_query_returns_written_node():
    await srv.brain_write(content="searchable content", tags=["t1"])
    response = await srv.brain_query(query="searchable")
    assert isinstance(response, CompiledContextResponse)
    assert response.total_matches == 1
    assert response.returned_count == 1
    assert response.items[0].content == "searchable content"


async def test_brain_query_with_tag_filter():
    await srv.brain_write(content="alpha", tags=["a"])
    await srv.brain_write(content="alpha", tags=["b"])
    response = await srv.brain_query(query="alpha", tags=["a"])
    assert response.total_matches == 1
    assert response.items[0].tags == ["a"]


async def test_brain_write_rejects_empty_content():
    with pytest.raises(InputValidationError, match="content must not be empty"):
        await srv.brain_write(content="", tags=["t"])


async def test_brain_write_rejects_empty_tags():
    with pytest.raises(InputValidationError, match="at least one tag"):
        await srv.brain_write(content="x", tags=[])


async def test_brain_query_rejects_empty():
    with pytest.raises(InputValidationError, match="query must not be empty"):
        await srv.brain_query(query="")


async def test_brain_write_round_trips_via_call_tool():
    written = await srv.mcp.call_tool(
        "brain_write",
        {"content": "via call_tool", "tags": ["x"]},
    )
    if isinstance(written, tuple):
        _, structured = written
        assert structured["node"]["content"] == "via call_tool"
    elif isinstance(written, dict):
        assert written["node"]["content"] == "via call_tool"
    else:
        pytest.fail(f"unexpected call_tool return type: {type(written).__name__}")
