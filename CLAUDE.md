# Knowledge Brain — MVP

Persistent memory layer for AI agents. Stores knowledge nodes in SQLite, exposed
to Claude via MCP and to humans via a `brain` CLI.

**This is the MVP.** Do not add features beyond what's currently implemented
without explicit approval from the maintainer.

## Long-term direction

The full design is in the sibling repo:
- `../project/docs/superpowers/specs/2026-04-18-knowledge-brain-design.md`
- `../project/docs/superpowers/specs/2026-04-25-system-architecture.md`

These describe edges, knowledge types, embeddings, retrieval logs, plugins, and
self-maintenance. **None of that is in scope here.** When tempted, ask first.

## Conventions

- Python 3.12+, type hints everywhere, `from __future__ import annotations`
- Pydantic v2 for all data models — deterministic JSON output is required
- TDD: failing test → minimal implementation → green → commit
- One responsibility per file; no premature abstractions
- Lint with `ruff check`; format with `ruff format`
- Tests must pass on every commit to `main`

## Toolchain

- `uv` manages Python (3.14 currently) and dependencies
- `uv sync --extra dev` installs everything
- `uv run pytest` runs tests
- `uv run ruff check .` and `uv run ruff format --check .` lint
