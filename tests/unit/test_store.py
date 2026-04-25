from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from knowledge_brain.models import KnowledgeNode
from knowledge_brain.store import Store


@pytest.fixture
def store(tmp_db_path: Path) -> Store:
    s = Store(tmp_db_path)
    s.init_schema()
    return s


def _node(content: str, tags: list[str], created_at: str = "2026-01-01T00:00:00+00:00", **kw):
    return KnowledgeNode(content=content, tags=tags, created_at=created_at, **kw)


class TestSchema:
    def test_init_schema_creates_db_file(self, tmp_db_path: Path):
        Store(tmp_db_path).init_schema()
        assert tmp_db_path.exists()

    def test_init_schema_creates_parent_dirs(self, tmp_path: Path):
        nested = tmp_path / "a" / "b" / "c" / "k.db"
        Store(nested).init_schema()
        assert nested.exists()

    def test_init_schema_is_idempotent(self, tmp_db_path: Path):
        s = Store(tmp_db_path)
        s.init_schema()
        s.init_schema()  # must not raise

    def test_check_constraint_rejects_bad_confidence(self, store: Store):
        with sqlite3.connect(store.db_path) as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO knowledge_nodes "
                    "(id, content, tags, source_type, source_ref, created_at, confidence) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("kn-bad", "x", "[]", "session", "", "2026-01-01T00:00:00+00:00", 1.5),
                )

    def test_check_constraint_rejects_bad_source_type(self, store: Store):
        with sqlite3.connect(store.db_path) as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO knowledge_nodes "
                    "(id, content, tags, source_type, source_ref, created_at, confidence) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("kn-bad2", "x", "[]", "bogus", "", "2026-01-01T00:00:00+00:00", 0.5),
                )


class TestWriteAndQuery:
    def test_write_then_query_returns_node(self, store: Store):
        node = _node("hello world", ["t1"])
        store.write_node(node)
        items, total = store.query()
        assert total == 1
        assert items == [node]

    def test_query_text_is_case_insensitive(self, store: Store):
        store.write_node(_node("Hello World", ["t"]))
        for q in ("hello", "HELLO", "Hello", "WORLD"):
            items, _ = store.query(query_text=q)
            assert len(items) == 1, f"query={q!r} returned no match"

    def test_query_text_escapes_like_wildcards(self, store: Store):
        store.write_node(
            _node("contains literal 50% string", ["t"], created_at="2026-01-02T00:00:00+00:00")
        )
        store.write_node(
            _node("no special chars here", ["t"], created_at="2026-01-01T00:00:00+00:00")
        )
        items, _ = store.query(query_text="50%")
        assert len(items) == 1
        assert "50%" in items[0].content

    def test_query_text_escapes_underscore(self, store: Store):
        store.write_node(
            _node("snake_case identifier", ["t"], created_at="2026-01-02T00:00:00+00:00")
        )
        store.write_node(
            _node("snakeXcase identifier", ["t"], created_at="2026-01-01T00:00:00+00:00")
        )
        items, _ = store.query(query_text="snake_case")
        assert len(items) == 1
        assert "snake_case" in items[0].content

    def test_query_tags_requires_all(self, store: Store):
        store.write_node(_node("a", ["t1", "t2"], created_at="2026-01-03T00:00:00+00:00"))
        store.write_node(_node("b", ["t1"], created_at="2026-01-02T00:00:00+00:00"))
        store.write_node(_node("c", ["t2"], created_at="2026-01-01T00:00:00+00:00"))
        items, total = store.query(tags=["t1", "t2"])
        assert total == 1
        assert items[0].content == "a"

    def test_query_tags_match_whole_value_not_substring(self, store: Store):
        store.write_node(_node("x", ["foo-bar"]))
        items, total = store.query(tags=["foo"])
        assert total == 0
        assert items == []

    def test_query_combines_text_and_tags(self, store: Store):
        store.write_node(_node("matching content", ["t1"], created_at="2026-01-03T00:00:00+00:00"))
        store.write_node(_node("matching content", ["t2"], created_at="2026-01-02T00:00:00+00:00"))
        store.write_node(_node("other content", ["t1"], created_at="2026-01-01T00:00:00+00:00"))
        items, total = store.query(query_text="matching", tags=["t1"])
        assert total == 1
        assert items[0].content == "matching content"
        assert "t1" in items[0].tags

    def test_results_ordered_by_created_at_desc(self, store: Store):
        store.write_node(_node("old", ["t"], created_at="2026-01-01T00:00:00+00:00"))
        store.write_node(_node("new", ["t"], created_at="2026-03-01T00:00:00+00:00"))
        store.write_node(_node("mid", ["t"], created_at="2026-02-01T00:00:00+00:00"))
        items, _ = store.query()
        assert [n.content for n in items] == ["new", "mid", "old"]

    def test_limit_caps_results_total_matches_unbounded(self, store: Store):
        for i in range(15):
            store.write_node(
                _node(f"n{i}", ["t"], created_at=f"2026-01-{i + 1:02d}T00:00:00+00:00")
            )
        items, total = store.query(limit=5)
        assert total == 15
        assert len(items) == 5

    def test_query_returns_empty_for_no_matches(self, store: Store):
        store.write_node(_node("x", ["t"]))
        items, total = store.query(query_text="nope")
        assert items == []
        assert total == 0

    def test_query_round_trips_all_fields(self, store: Store):
        node = KnowledgeNode(
            content="full",
            tags=["a", "b"],
            source_type="ingestion",
            source_ref="paper:42",
            confidence=0.42,
        )
        store.write_node(node)
        items, _ = store.query()
        assert items[0] == node
