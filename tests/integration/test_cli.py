from __future__ import annotations

import json
from pathlib import Path

import pytest

from knowledge_brain.cli.main import main


def _run(argv: list[str], capsys) -> tuple[int, str, str]:
    rc = main(argv)
    captured = capsys.readouterr()
    return rc, captured.out, captured.err


class TestInit:
    def test_init_creates_db(self, tmp_db_path: Path, capsys):
        rc, out, _ = _run(["--db-path", str(tmp_db_path), "init"], capsys)
        assert rc == 0
        assert tmp_db_path.exists()
        assert str(tmp_db_path) in out

    def test_init_refuses_existing_db(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        rc, _, err = _run(["--db-path", str(tmp_db_path), "init"], capsys)
        assert rc == 1
        assert "already exists" in err

    def test_init_force_recreates(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        rc, _, _ = _run(["--db-path", str(tmp_db_path), "init", "--force"], capsys)
        assert rc == 0


class TestWrite:
    def _init(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)

    def test_write_happy_path_prints_id(self, tmp_db_path: Path, capsys):
        self._init(tmp_db_path, capsys)
        rc, out, _ = _run(
            ["--db-path", str(tmp_db_path), "write", "hello world", "--tags", "t1,t2"],
            capsys,
        )
        assert rc == 0
        assert out.strip().startswith("kn-")

    def test_write_rejects_empty_content(self, tmp_db_path: Path, capsys):
        self._init(tmp_db_path, capsys)
        rc, _, err = _run(
            ["--db-path", str(tmp_db_path), "write", "   ", "--tags", "t1"],
            capsys,
        )
        assert rc == 1
        assert "content must not be empty" in err

    def test_write_rejects_when_tags_resolve_empty(self, tmp_db_path: Path, capsys):
        self._init(tmp_db_path, capsys)
        rc, _, err = _run(
            ["--db-path", str(tmp_db_path), "write", "x", "--tags", " , , "],
            capsys,
        )
        assert rc == 1
        assert "at least one tag" in err

    def test_write_rejects_oversize_content(self, tmp_db_path: Path, capsys):
        self._init(tmp_db_path, capsys)
        long = " ".join(["w"] * 200)
        rc, _, err = _run(
            [
                "--db-path",
                str(tmp_db_path),
                "write",
                long,
                "--tags",
                "t",
                "--max-input-tokens",
                "10",
            ],
            capsys,
        )
        assert rc == 1
        assert "exceeds max_input_tokens" in err


class TestQuery:
    def _setup(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        _run(
            ["--db-path", str(tmp_db_path), "write", "alpha story", "--tags", "story,a"],
            capsys,
        )
        _run(
            ["--db-path", str(tmp_db_path), "write", "beta story", "--tags", "story,b"],
            capsys,
        )

    def test_query_text_returns_json(self, tmp_db_path: Path, capsys):
        self._setup(tmp_db_path, capsys)
        rc, out, _ = _run(["--db-path", str(tmp_db_path), "query", "alpha"], capsys)
        assert rc == 0
        payload = json.loads(out)
        assert payload["query"] == "alpha"
        assert payload["total_matches"] == 1
        assert payload["returned_count"] == 1
        assert payload["items"][0]["content"] == "alpha story"

    def test_query_with_tags_filters(self, tmp_db_path: Path, capsys):
        self._setup(tmp_db_path, capsys)
        rc, out, _ = _run(
            ["--db-path", str(tmp_db_path), "query", "story", "--tags", "a"],
            capsys,
        )
        assert rc == 0
        payload = json.loads(out)
        assert payload["total_matches"] == 1
        assert payload["items"][0]["content"] == "alpha story"

    def test_query_no_match_empty_items(self, tmp_db_path: Path, capsys):
        self._setup(tmp_db_path, capsys)
        rc, out, _ = _run(["--db-path", str(tmp_db_path), "query", "zeta"], capsys)
        assert rc == 0
        payload = json.loads(out)
        assert payload["items"] == []
        assert payload["total_matches"] == 0

    def test_query_rejects_empty(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        rc, _, err = _run(["--db-path", str(tmp_db_path), "query", "   "], capsys)
        assert rc == 1
        assert "query must not be empty" in err


class TestList:
    def test_list_returns_json_array(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        _run(["--db-path", str(tmp_db_path), "write", "a", "--tags", "t"], capsys)
        _run(["--db-path", str(tmp_db_path), "write", "b", "--tags", "t"], capsys)
        rc, out, _ = _run(["--db-path", str(tmp_db_path), "list"], capsys)
        assert rc == 0
        payload = json.loads(out)
        assert isinstance(payload, list)
        assert len(payload) == 2

    def test_list_respects_limit(self, tmp_db_path: Path, capsys):
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        for i in range(5):
            _run(
                ["--db-path", str(tmp_db_path), "write", f"n{i}", "--tags", "t"],
                capsys,
            )
        rc, out, _ = _run(["--db-path", str(tmp_db_path), "list", "--limit", "2"], capsys)
        assert rc == 0
        payload = json.loads(out)
        assert len(payload) == 2


class TestParser:
    def test_unknown_subcommand_errors(self, capsys):
        with pytest.raises(SystemExit):
            main(["bogus"])
