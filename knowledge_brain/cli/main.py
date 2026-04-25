from __future__ import annotations

import argparse
import sys

from ..models import InputValidationError
from . import init as init_cmd
from . import list as list_cmd
from . import query as query_cmd
from . import write as write_cmd


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brain", description="Knowledge Brain MVP")
    p.add_argument(
        "--db-path",
        default="data_store/knowledge.db",
        help="Path to SQLite DB (default: data_store/knowledge.db)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    for mod in (init_cmd, write_cmd, query_cmd, list_cmd):
        mod.register(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except InputValidationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
