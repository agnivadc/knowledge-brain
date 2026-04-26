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
        payload = json.loads(out)
        assert payload["id"].startswith("kn-")
        assert payload["content"] == "hello world"
        assert payload["tags"] == ["t1", "t2"]

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

    def test_write_to_uninitialized_db_exits_2(self, tmp_path: Path, capsys):
        db = tmp_path / "noinit.db"
        # No init - table doesn't exist; triggers sqlite3.OperationalError
        rc, _, err = _run(
            ["--db-path", str(db), "write", "hello", "--tags", "t"],
            capsys,
        )
        assert rc == 2
        assert "storage error" in err


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


class TestExportImport:
    def _seed(self, tmp_db_path: Path, capsys, n: int = 3) -> list[str]:
        _run(["--db-path", str(tmp_db_path), "init"], capsys)
        ids = []
        for i in range(n):
            _, out, _ = _run(
                [
                    "--db-path",
                    str(tmp_db_path),
                    "write",
                    f"content {i}",
                    "--tags",
                    f"tag-{i}",
                ],
                capsys,
            )
            ids.append(json.loads(out.strip())["id"])
        return ids

    def test_export_writes_one_jsonl_line_per_node(self, tmp_db_path: Path, tmp_path: Path, capsys):
        self._seed(tmp_db_path, capsys, n=3)
        out_path = tmp_path / "k.jsonl"
        rc, out, _ = _run(
            ["--db-path", str(tmp_db_path), "export", str(out_path)], capsys
        )
        assert rc == 0
        assert "exported 3 node(s)" in out
        lines = out_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 3
        for line in lines:
            assert json.loads(line)["content"].startswith("content ")

    def test_export_lines_sorted_by_id(self, tmp_db_path: Path, tmp_path: Path, capsys):
        self._seed(tmp_db_path, capsys, n=5)
        out_path = tmp_path / "k.jsonl"
        _run(["--db-path", str(tmp_db_path), "export", str(out_path)], capsys)
        ids = [json.loads(l)["id"] for l in out_path.read_text("utf-8").splitlines()]
        assert ids == sorted(ids)

    def test_export_creates_parent_dirs(self, tmp_db_path: Path, tmp_path: Path, capsys):
        self._seed(tmp_db_path, capsys, n=1)
        nested = tmp_path / "a" / "b" / "c.jsonl"
        rc, _, _ = _run(
            ["--db-path", str(tmp_db_path), "export", str(nested)], capsys
        )
        assert rc == 0
        assert nested.exists()

    def test_round_trip_preserves_all_nodes(self, tmp_path: Path, capsys):
        src_db = tmp_path / "src.db"
        dst_db = tmp_path / "dst.db"
        jsonl = tmp_path / "k.jsonl"

        ids = self._seed(src_db, capsys, n=4)
        _run(["--db-path", str(src_db), "export", str(jsonl)], capsys)

        rc, out, _ = _run(
            ["--db-path", str(dst_db), "import", str(jsonl)], capsys
        )
        assert rc == 0
        assert "4 inserted" in out

        # Re-export from dst should yield byte-identical jsonl
        jsonl2 = tmp_path / "k2.jsonl"
        _run(["--db-path", str(dst_db), "export", str(jsonl2)], capsys)
        assert jsonl.read_text("utf-8") == jsonl2.read_text("utf-8")

        # All seeded ids made it through
        dst_ids = {json.loads(l)["id"] for l in jsonl2.read_text("utf-8").splitlines()}
        assert dst_ids == set(ids)

    def test_import_skips_existing_ids_by_default(self, tmp_path: Path, capsys):
        src_db = tmp_path / "src.db"
        jsonl = tmp_path / "k.jsonl"
        self._seed(src_db, capsys, n=2)
        _run(["--db-path", str(src_db), "export", str(jsonl)], capsys)

        # Import twice into the same DB; second pass should skip everything
        rc, _, _ = _run(["--db-path", str(src_db), "import", str(jsonl)], capsys)
        assert rc == 0
        rc, out, _ = _run(["--db-path", str(src_db), "import", str(jsonl)], capsys)
        assert rc == 0
        assert "0 inserted" in out
        assert "2 skipped" in out

    def test_import_force_replaces_existing(self, tmp_path: Path, capsys):
        src_db = tmp_path / "src.db"
        jsonl = tmp_path / "k.jsonl"
        self._seed(src_db, capsys, n=2)
        _run(["--db-path", str(src_db), "export", str(jsonl)], capsys)

        rc, out, _ = _run(
            ["--db-path", str(src_db), "import", str(jsonl), "--force"], capsys
        )
        assert rc == 0
        assert "2 replaced" in out

    def test_import_handles_blank_lines(self, tmp_path: Path, capsys):
        src_db = tmp_path / "src.db"
        jsonl = tmp_path / "k.jsonl"
        self._seed(src_db, capsys, n=2)
        _run(["--db-path", str(src_db), "export", str(jsonl)], capsys)
        # Inject blank lines
        original = jsonl.read_text("utf-8")
        jsonl.write_text("\n" + original + "\n\n", encoding="utf-8")

        dst_db = tmp_path / "dst.db"
        rc, out, _ = _run(
            ["--db-path", str(dst_db), "import", str(jsonl)], capsys
        )
        assert rc == 0
        assert "2 inserted" in out

    def test_import_errors_on_missing_file(self, tmp_path: Path, capsys):
        rc, out, _ = _run(
            ["--db-path", str(tmp_path / "k.db"), "import", str(tmp_path / "nope.jsonl")],
            capsys,
        )
        assert rc == 1
        assert "does not exist" in out

    def test_import_errors_on_malformed_line(self, tmp_path: Path, capsys):
        jsonl = tmp_path / "bad.jsonl"
        jsonl.write_text("not valid json\n", encoding="utf-8")
        rc, out, _ = _run(
            ["--db-path", str(tmp_path / "k.db"), "import", str(jsonl)], capsys
        )
        assert rc == 1
        assert "line 1" in out


class TestParser:
    def test_unknown_subcommand_errors(self, capsys):
        with pytest.raises(SystemExit):
            main(["bogus"])
