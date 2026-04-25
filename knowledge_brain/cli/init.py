from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..store import Store


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="Initialize the knowledge DB")
    p.add_argument("--force", action="store_true", help="Recreate DB even if it exists")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    db_path = Path(args.db_path)
    if db_path.exists() and not args.force:
        print(
            f"error: {db_path} already exists. Use --force to recreate.",
            file=sys.stderr,
        )
        return 1
    if db_path.exists() and args.force:
        db_path.unlink()
    Store(db_path).init_schema()
    print(f"Initialized {db_path}")
    return 0
