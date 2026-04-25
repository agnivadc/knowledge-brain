# Knowledge Brain — MVP

Persistent memory layer for AI agents. Stores knowledge nodes in SQLite, exposes
them to Claude via MCP and to humans via a `brain` CLI.

## Install

```bash
uv sync --extra dev
# or:  pip install -e .[dev]
```

## Use

```bash
brain init                                       # creates data_store/knowledge.db
brain write "MES Supertrend uses ATR=14" --tags strategy,mes
brain query "supertrend"                         # text search
brain query "supertrend" --tags strategy         # tag-filtered text search
brain list --limit 5                             # most-recent nodes
```

## MCP server

Run `brain-mcp` (stdio). Set `BRAIN_DB_PATH` env var to point at your DB.
The server exposes two tools: `brain_write` and `brain_query`.

To wire it into Claude Code or Claude Desktop, see `docs/mcp-setup.md`.

## Status

This is the MVP. See `CLAUDE.md` for what's intentionally out of scope.
