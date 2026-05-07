from __future__ import annotations

import argparse
import sqlite3
import sys

from ..models import InputValidationError
from . import export as export_cmd
from . import import_jsonl as import_cmd
from . import init as init_cmd
from . import list as list_cmd
from . import query as query_cmd
from . import write as write_cmd

PROTOCOL_VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brain", description="Knowledge Brain MVP")
    p.add_argument(
        "--db-path",
        default="data_store/knowledge.db",
        help="Path to SQLite DB (default: data_store/knowledge.db)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    for mod in (init_cmd, write_cmd, query_cmd, list_cmd, export_cmd, import_cmd):
        mod.register(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    if "--protocol-version" in args_list:
        print(PROTOCOL_VERSION)
        return 0
    args = build_parser().parse_args(args_list)
    try:
        return args.func(args)
    except InputValidationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f"storage error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
