from __future__ import annotations

import argparse
from pathlib import Path

from ..models import CompiledContextResponse
from ..quality import validate_query_input
from ..store import Store


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
    validate_query_input(args.query, args.max_input_tokens)
    tags = _parse_tags(args.tags)
    items, total = Store(Path(args.db_path)).query(
        query_text=args.query, tags=tags, limit=args.limit
    )
    response = CompiledContextResponse(
        query=args.query,
        items=items,
        total_matches=total,
        returned_count=len(items),
    )
    print(response.model_dump_json(indent=2))
    return 0
