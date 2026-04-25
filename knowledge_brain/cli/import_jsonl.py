from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..models import KnowledgeNode
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

    counts = {"inserted": 0, "skipped": 0, "replaced": 0}
    with src.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                node = KnowledgeNode(**data)
            except Exception as e:
                print(f"error: line {line_no}: {e}", flush=True)
                return 1
            counts[store.merge_node(node, force=args.force)] += 1

    print(
        f"import complete: {counts['inserted']} inserted, "
        f"{counts['skipped']} skipped, {counts['replaced']} replaced"
    )
    return 0
