from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..store import Store


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "export",
        help="Export all nodes to JSONL (one node per line, sorted by id)",
    )
    p.add_argument("path", help="Output JSONL path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    nodes = Store(Path(args.db_path)).all_nodes()
    out = Path(args.path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for n in nodes:
            f.write(json.dumps(n.model_dump(mode="json"), sort_keys=True))
            f.write("\n")
    print(f"exported {len(nodes)} node(s) to {out}")
    return 0
