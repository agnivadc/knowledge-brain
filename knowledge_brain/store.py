from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .models import KnowledgeNode

SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id          TEXT PRIMARY KEY,
    content     TEXT NOT NULL,
    tags        TEXT NOT NULL DEFAULT '[]',
    source_type TEXT NOT NULL CHECK(source_type IN ('session', 'human', 'ingestion')),
    source_ref  TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL,
    confidence  REAL NOT NULL DEFAULT 0.7 CHECK(confidence BETWEEN 0.0 AND 1.0)
);
CREATE INDEX IF NOT EXISTS idx_kn_created ON knowledge_nodes(created_at);
CREATE INDEX IF NOT EXISTS idx_kn_source  ON knowledge_nodes(source_type);
"""

_COLS = "id, content, tags, source_type, source_ref, created_at, confidence"


def _escape_like(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _row_to_node(r: tuple) -> KnowledgeNode:
    return KnowledgeNode(
        id=r[0],
        content=r[1],
        tags=json.loads(r[2]),
        source_type=r[3],
        source_ref=r[4],
        created_at=r[5],
        confidence=r[6],
    )


class Store:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def init_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def write_node(self, node: KnowledgeNode) -> None:
        with self._connect() as conn:
            conn.execute(
                f"INSERT INTO knowledge_nodes ({_COLS}) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    node.id,
                    node.content,
                    json.dumps(node.tags),
                    node.source_type,
                    node.source_ref,
                    node.created_at,
                    node.confidence,
                ),
            )

    def query(
        self,
        query_text: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> tuple[list[KnowledgeNode], int]:
        where: list[str] = []
        params: list = []
        if query_text:
            where.append("LOWER(content) LIKE LOWER(?) ESCAPE '\\'")
            params.append(f"%{_escape_like(query_text)}%")
        if tags:
            for tag in tags:
                where.append("EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)")
                params.append(tag)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        with self._connect() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM knowledge_nodes{clause}", params
            ).fetchone()[0]
            rows = conn.execute(
                f"SELECT {_COLS} FROM knowledge_nodes{clause} ORDER BY created_at DESC LIMIT ?",
                [*params, limit],
            ).fetchall()
        return [_row_to_node(r) for r in rows], total
