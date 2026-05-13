from __future__ import annotations

import argparse
from pathlib import Path

from ..jsonl import JsonlNodeDecodeError, format_import_summary, import_nodes_from_lines
from ..store import Store


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "import",
        help="Import nodes from JSONL; existing IDs are skipped unless --force",
    )
    p.add_argument("path", help="Input JSONL path")
    p.add_argument(
        "--force",
        action="store_true",
        help="Replace existing nodes when IDs collide (default: skip)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    src = Path(args.path)
    if not src.exists():
        print(f"error: {src} does not exist", flush=True)
        return 1

    store = Store(Path(args.db_path))
    store.init_schema()

    try:
        with src.open(encoding="utf-8") as f:
            summary = import_nodes_from_lines(f, store, force=args.force)
    except JsonlNodeDecodeError as e:
        print(f"error: {e}", flush=True)
        return 1

    print(format_import_summary(summary))
    return 0
