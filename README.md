# knowledge-brain

Persistent memory for AI agents. Notes written in one session are available in the next — across projects, across tools, across restarts.

Works as a CLI tool and as an MCP server (for Claude Code, GitHub Copilot, and any MCP-compatible host).

---

## What problem does this solve?

AI assistants forget everything when a session ends. If you told your AI assistant about your coding style last week, you have to tell it again today. If it discovered something useful about your project, that knowledge disappears.

`knowledge-brain` gives AI assistants a place to store notes that survive restarts. The AI writes a note; next session it reads it back. You see exactly what is stored and can manage it yourself.

---

## How it works

Notes are stored in a local SQLite file on your machine — nothing leaves your computer unless you put it there.

Two storage scopes:

| Scope | Where | When to use |
|---|---|---|
| **Global** (recommended for personal use) | `~/.knowledge-brain/knowledge.db` | Notes useful across all your projects (coding style, preferences, machine setup) |
| **Project-local** | `data_store/knowledge.db` in your project | Notes that belong to one project only |

---

## Prerequisites

- **Python 3.12+** — check with `python3 --version`
- **uv** — fast Python package manager

Install `uv` if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Installation

### As a CLI tool (run directly, no install needed)

```bash
# Initialize global memory once
uvx --from git+https://github.com/agnivadc/knowledge-brain.git \
  brain --db-path ~/.knowledge-brain/knowledge.db init

# Set the path in your shell profile so you don't have to type it every time
echo 'export BRAIN_DB_PATH="$HOME/.knowledge-brain/knowledge.db"' >> ~/.zshrc
source ~/.zshrc
```

### As a developer (clone the repo)

```bash
git clone https://github.com/agnivadc/knowledge-brain.git
cd knowledge-brain
uv sync --extra dev
uv run brain --db-path data_store/knowledge.db init
```

---

## CLI Reference

All commands accept `--db-path <path>` to choose which database to use. If you set `BRAIN_DB_PATH`, you can omit it.

### `brain init`

Creates the database file.

```bash
brain init
# or
brain --db-path ~/.knowledge-brain/knowledge.db init
```

### `brain write`

Saves a note.

```bash
brain write "This project uses tabs, not spaces." --tags style,python
brain write "Deploy target is AWS us-east-1." --tags infra,aws
brain write "Auth uses JWT tokens, 1 hour expiry." --tags auth
```

### `brain query`

Searches for notes by keywords.

```bash
brain query "coding style"
# Returns notes that mention coding style

brain query "deploy"
# Returns notes tagged with deploy or mentioning deploy
```

### `brain list`

Shows all stored notes.

```bash
brain list
```

### `brain export`

Exports all notes to a JSON Lines file.

```bash
brain export --output backup.jsonl
```

### `brain import`

Imports notes from a JSON Lines file.

```bash
brain import backup.jsonl
```

---

## MCP Server (for AI assistants)

MCP lets AI tools like Claude Code use `knowledge-brain` directly — no manual copy-paste needed. The AI writes notes with `brain_write` and retrieves them with `brain_query` as part of its normal workflow.

### Claude Code

```bash
claude mcp add knowledge-brain \
  --scope user \
  --env BRAIN_DB_PATH="$HOME/.knowledge-brain/knowledge.db" \
  -- uvx --from git+https://github.com/agnivadc/knowledge-brain.git brain-mcp
```

Restart Claude Code. The tools `brain_write` and `brain_query` appear automatically in Claude's tool list.

### GitHub Copilot

In Copilot settings, enable MCP and add the same `brain-mcp` server command:
```
uvx --from git+https://github.com/agnivadc/knowledge-brain.git brain-mcp
```
Set environment variable `BRAIN_DB_PATH` to your global database path.

### OpenAI Codex / Pi

These use the `brain` CLI directly as a bash tool. Set `BRAIN_DB_PATH` in your shell profile:
```bash
export BRAIN_DB_PATH="$HOME/.knowledge-brain/knowledge.db"
```
No extra config needed — the AI calls `brain write` and `brain query` in its bash tool.

---

## What gets stored and what doesn't

**Good things to store:**
- Your preferred coding style, naming conventions, patterns
- Project decisions and the reasoning behind them
- Machine setup notes, tool versions, paths
- Facts you want available in every session

**Things to avoid storing:**
- Temporary or in-progress work (use a scratch file instead)
- Secrets, passwords, or tokens
- Implementation details that change often
- Anything you wouldn't want mixed into unrelated projects

---

## Example session

```bash
# Claude Code session 1
# Claude writes a note after learning something:
brain write "Project uses Pydantic v2. All models must inherit from BaseModel." --tags project,pydantic

# Claude Code session 2 (next day, new session)
# Claude queries memory before starting:
brain query "pydantic"
# Retrieves: "Project uses Pydantic v2..."
# Claude now knows this without being told again.
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `brain: command not found` | Not installed or not in PATH | Use `uvx --from git+... brain` or add uv bin dir to PATH |
| `brain_write` / `brain_query` missing in Claude Code | MCP server not registered | Run the `claude mcp add` command above, then restart Claude Code |
| Query returns nothing for a note you just wrote | CLI and MCP pointing at different DB files | Make sure `BRAIN_DB_PATH` is the same absolute path in your shell and in the MCP config |
| `database is locked` error | Two processes writing at the same time | Retry — the write will go through once the lock releases |
| First `uvx` run is slow | Downloading and caching the package | Subsequent runs are fast (cache at `~/.cache/uv/`) |

---

## How it connects to Agent OS

[context_os](https://github.com/algoSiliguri/context_os) uses `knowledge-brain` as its memory substrate. When an AI session is active under Agent OS, memory reads and writes are routed through `knowledge-brain` automatically — either to a global store or to a project-local store, depending on your manifest settings.

You don't need Agent OS to use `knowledge-brain` — it works standalone. But if you want full session governance (binding, approval flows, event logging), use both together.
