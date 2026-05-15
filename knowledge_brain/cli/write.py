from __future__ import annotations

import argparse
from ..operations import BrainOperations


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("write", help="Write a knowledge node")
    p.add_argument("content", help="Content of the knowledge node")
    p.add_argument(
        "--tags",
        required=True,
        help="Comma-separated list of tags (at least one)",
    )
    p.add_argument(
        "--source-type",
        choices=["session", "human", "ingestion"],
        default="human",
        help="Source type (default: human)",
    )
    p.add_argument("--source-ref", default="", help="Optional source reference string")
    p.add_argument("--confidence", type=float, default=0.7, help="Confidence in [0,1]")
    p.add_argument(
        "--max-input-tokens",
        type=int,
        default=2000,
        help="Reject content over this many approximate tokens (default: 2000)",
    )
    p.set_defaults(func=run)


def _parse_tags(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]


def run(args: argparse.Namespace) -> int:
    tags = _parse_tags(args.tags)
    result = BrainOperations.from_db(args.db_path).write(
        content=args.content,
        tags=tags,
        source_type=args.source_type,
        source_ref=args.source_ref,
        confidence=args.confidence,
        max_input_tokens=args.max_input_tokens,
    )
    print(result.node.model_dump_json())
    return 0
