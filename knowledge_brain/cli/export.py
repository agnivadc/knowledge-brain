from __future__ import annotations

import argparse
from pathlib import Path

from ..jsonl import encode_nodes
from ..operations import BrainOperations


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "export",
        help="Export all nodes to JSONL (one node per line, sorted by id)",
    )
    p.add_argument("path", help="Output JSONL path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    nodes = BrainOperations.from_db(args.db_path).export()
    out = Path(args.path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for line in encode_nodes(nodes):
            f.write(line)
            f.write("\n")
    print(f"exported {len(nodes)} node(s) to {out}")
    return 0
