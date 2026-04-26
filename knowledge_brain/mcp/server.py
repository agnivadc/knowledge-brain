from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from ..models import CompiledContextResponse, KnowledgeNode, WriteResult
from ..quality import validate_query_input, validate_write_input
from ..store import Store

mcp = FastMCP("knowledge-brain")


def _store() -> Store:
    return Store(Path(os.environ.get("BRAIN_DB_PATH", "data_store/knowledge.db")))


@mcp.tool()
async def brain_write(
    content: str,
    tags: list[str],
    source_type: Literal["session", "human", "ingestion"] = "session",
    source_ref: str = "",
    confidence: float = 0.7,
    max_input_tokens: int = 2000,
) -> WriteResult:
    """Write a knowledge node to the brain. Returns the persisted node."""
    validate_write_input(content, tags, max_input_tokens)
    node = KnowledgeNode(
        content=content,
        tags=tags,
        source_type=source_type,
        source_ref=source_ref,
        confidence=confidence,
    )
    _store().write_node(node)
    return WriteResult(node=node)


@mcp.tool()
async def brain_query(
    query: str,
    tags: list[str] | None = None,
    max_input_tokens: int = 500,
    max_results: int = 10,
) -> CompiledContextResponse:
    """Query the brain by tag and/or text match. Returns top-N most-recent items."""
    validate_query_input(query, max_input_tokens)
    items, total = _store().query(query_text=query, tags=tags, limit=max_results)
    return CompiledContextResponse(
        query=query,
        items=items,
        total_matches=total,
        returned_count=len(items),
    )


@mcp.tool()
async def brain_export() -> list[KnowledgeNode]:
    """Export all knowledge nodes. Used for backup and cross-session sync."""
    return _store().all_nodes()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
