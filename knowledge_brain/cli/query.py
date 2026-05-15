from __future__ import annotations

import argparse
from ..operations import BrainOperations


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("query", help="Query the knowledge brain")
    p.add_argument("query", help="Search text")
    p.add_argument("--tags", default="", help="Comma-separated tag filter (AND across tags)")
    p.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    p.add_argument(
        "--max-input-tokens",
        type=int,
        default=500,
        help="Reject queries over this many tokens (default: 500)",
    )
    p.set_defaults(func=run)


def _parse_tags(raw: str) -> list[str] | None:
    tags = [t.strip() for t in raw.split(",") if t.strip()]
    return tags or None


def run(args: argparse.Namespace) -> int:
    tags = _parse_tags(args.tags)
    response = BrainOperations.from_db(args.db_path).query(
        query=args.query,
        tags=tags,
        max_input_tokens=args.max_input_tokens,
        max_results=args.limit,
    )
    print(response.model_dump_json(indent=2))
    return 0
