# Knowledge Brain

Knowledge Brain is a small persistent memory layer for AI agents.

It stores notes in SQLite and exposes the same data in two ways:
- a `brain` command-line tool for humans and scripts
- an MCP server for Claude and other MCP clients

## What knowledge-brain Is

`knowledge-brain` is a simple place to keep durable facts, decisions, and other useful notes.

It is not a full agent runtime.
It does one job: save and find memory entries in a predictable way.

## Why Memory Is Separate From The Runtime

Keeping memory separate from the runtime makes the system easier to reason about.

The runtime can start, stop, or change without losing the stored knowledge.
The memory database can also be shared across tools without tying it to one specific agent process.

## Two Kinds Of Memory

This project is designed to work with two broad memory scopes:

- project-local memory: only for one project
- global memory: shared across projects on the same machine

The same CLI and MCP tools can work with either scope. The difference is which database path you point them at.

## The Safe Default

The safe default is project-local memory.

That means new notes stay with the project unless you explicitly choose a different database path.
This reduces accidental sharing and keeps project history isolated.

## Tiny Example

```bash
brain init
brain write "This project uses project-local memory by default." --tags project,example
brain query "project-local memory"
```

## How It Connects To context_os

`context_os` uses Knowledge Brain as its persistent L3 memory backend.

In practice, `context_os` can point the `brain` CLI or MCP server at a project-local database for one repo, or at a global database when memory should follow you across projects.

## When To Use Global Memory

Use global memory when the note is personal, stable, and useful in many projects.

Good examples:
- your preferred coding conventions
- machine-specific setup notes
- recurring facts you want available everywhere

## When Not To Use Global Memory

Do not use global memory for project-specific or temporary information.

Avoid it for:
- one-off implementation details
- decisions that only matter in one repo
- draft ideas that may change soon
- anything you would not want visible in unrelated projects

## Install

```bash
uv sync --extra dev
# or:  pip install -e .[dev]
```

## MCP Server

Run `brain-mcp` over stdio. Set `BRAIN_DB_PATH` to point at the database you want to use.

The server exposes two tools:
- `brain_write`
- `brain_query`

To wire it into Claude Code or Claude Desktop, see `docs/mcp-setup.md`.

## Status

This is the MVP. See `CLAUDE.md` for what is intentionally out of scope.
