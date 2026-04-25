from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..store import Store


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("list", help="List recent knowledge nodes")
    p.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    items, _ = Store(Path(args.db_path)).query(limit=args.limit)
    print(json.dumps([n.model_dump(mode="json") for n in items], indent=2))
    return 0
