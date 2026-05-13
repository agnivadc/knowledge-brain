from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from ..models import CompiledContextResponse, KnowledgeNode, WriteResult
from ..operations import BrainOperations
from ..store import Store

mcp = FastMCP("knowledge-brain")


def _store() -> Store:
    return Store(Path(os.environ.get("BRAIN_DB_PATH", "data_store/knowledge.db")))


def _operations() -> BrainOperations:
    return BrainOperations(_store())


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
    return _operations().write(
        content=content,
        tags=tags,
        source_type=source_type,
        source_ref=source_ref,
        confidence=confidence,
        max_input_tokens=max_input_tokens,
    )


@mcp.tool()
async def brain_query(
    query: str,
    tags: list[str] | None = None,
    max_input_tokens: int = 500,
    max_results: int = 10,
) -> CompiledContextResponse:
    """Query the brain by tag and/or text match. Returns top-N most-recent items."""
    return _operations().query(
        query=query,
        tags=tags,
        max_input_tokens=max_input_tokens,
        max_results=max_results,
    )


@mcp.tool()
async def brain_export() -> list[KnowledgeNode]:
    """Export all knowledge nodes. Used for backup and cross-session sync."""
    return _operations().export()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
