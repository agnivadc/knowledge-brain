# MCP Setup

Wire the `brain-mcp` server into Claude clients so they can call `brain_write`
and `brain_query` as tools.

## Design choices (deterministic by construction)

- **One DB per workspace**, addressed by absolute path
- **`BRAIN_DB_PATH` env var** is the only way the server learns which DB to use
- **No auto-discovery, no defaults that depend on cwd, no fallback paths**

If the DB path is wrong or unset, the server fails fast. That's the point.

---

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — the only
  install tool you need; no manual venv management

`uv` ships `uvx`, which runs Python tools from a git URL or PyPI on demand
and caches them. We use it as the entry point for the MCP server.

---

## Quickstart (recommended): run via `uvx`

No clone, no venv, no path juggling.

### Initialize a database

Pick one absolute path and use it everywhere. Recommended location:

- macOS / Linux: `~/.knowledge-brain/knowledge.db`
- Windows: `%USERPROFILE%\.knowledge-brain\knowledge.db`

```bash
# macOS / Linux
mkdir -p ~/.knowledge-brain
uvx --from git+https://github.com/agnivadc/knowledge-brain.git \
  brain --db-path ~/.knowledge-brain/knowledge.db init
```

```powershell
# Windows
New-Item -ItemType Directory -Force "$HOME\.knowledge-brain" | Out-Null
uvx --from git+https://github.com/agnivadc/knowledge-brain.git `
  brain --db-path "$HOME\.knowledge-brain\knowledge.db" init
```

The DB is just a SQLite file; back it up like any other file.

---

## Claude Code (this CLI)

Add the server to your **user** scope so every project can use it:

```bash
# macOS / Linux
claude mcp add knowledge-brain \
  --scope user \
  --env BRAIN_DB_PATH="$HOME/.knowledge-brain/knowledge.db" \
  -- uvx --from git+https://github.com/agnivadc/knowledge-brain.git brain-mcp
```

```powershell
# Windows
claude mcp add knowledge-brain `
  --scope user `
  --env BRAIN_DB_PATH="$HOME\.knowledge-brain\knowledge.db" `
  -- uvx --from git+https://github.com/agnivadc/knowledge-brain.git brain-mcp
```

For a **project-scoped** server (committed to the repo, shared with
collaborators), use `--scope project` instead. The config lands in
`.mcp.json` in the project root.

Verify:

```bash
claude mcp list
```

You should see `knowledge-brain` listed. Restart Claude Code; the tools
`brain_write` and `brain_query` will appear in the tool list.

---

## Claude Desktop

Edit your config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

If the file doesn't exist, create it with exactly the content below. If it
does, merge the `knowledge-brain` entry into the existing `mcpServers`
object — leave other servers alone.

```json
{
  "mcpServers": {
    "knowledge-brain": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/agnivadc/knowledge-brain.git",
        "brain-mcp"
      ],
      "env": {
        "BRAIN_DB_PATH": "/absolute/path/to/knowledge.db"
      }
    }
  }
}
```

Replace `BRAIN_DB_PATH` with the absolute path you initialized above. On
Windows, JSON requires escaped backslashes:
`"BRAIN_DB_PATH": "C:\\Users\\<you>\\.knowledge-brain\\knowledge.db"`.

Restart Claude Desktop. The hammer/tools icon in the chat input should show
`brain_write` and `brain_query`.

---

## Verify end-to-end

1. In a Claude session, ask: *"Use brain_write to store: Knowledge Brain MVP shipped on 2026-04-25. Tags: brain, milestone."*
2. Then: *"Use brain_query to look up 'milestone'."*

The query should return the just-written node. If it returns 0 results, the
client and CLI are pointing at different DBs — double-check `BRAIN_DB_PATH`
matches in every place.

Cross-check from the terminal:

```bash
uvx --from git+https://github.com/agnivadc/knowledge-brain.git \
  brain --db-path ~/.knowledge-brain/knowledge.db list --limit 5
```

The same node should appear in the JSON output.

---

## From source (development install)

Use this only if you're working on the brain itself.

```bash
git clone https://github.com/agnivadc/knowledge-brain.git
cd knowledge-brain
uv sync --extra dev
```

Now `uv run brain ...` and `uv run brain-mcp` work against the local
checkout. To point Claude clients at the dev build, replace the `uvx
--from git+...` invocation in your config with the full path to the
checkout's venv binary, e.g.
`./knowledge-brain/.venv/bin/brain-mcp` (macOS/Linux) or
`.\knowledge-brain\.venv\Scripts\brain-mcp.exe` (Windows).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `uvx: command not found` | `uv` not installed | Install per https://docs.astral.sh/uv/getting-started/installation/ |
| Tool list empty after restart | Server failed to start | Run the `uvx ... brain-mcp` command manually in a terminal — it'll print the error |
| `brain_query` returns nothing for known data | Different DB than the CLI used | Make `BRAIN_DB_PATH` absolute and identical in every config |
| `error: data_store/knowledge.db already exists` | Default DB conflict | Always pass `--db-path` explicitly; never rely on cwd |
| First run is slow | `uvx` is downloading and caching the package | Subsequent runs are fast (cache lives in `~/.cache/uv/`) |

The MCP client launches `brain-mcp` as a subprocess and talks to it over
stdio. If the process can't start, the client logs the error. Log locations:

- Claude Desktop (macOS): `~/Library/Logs/Claude/`
- Claude Desktop (Windows): `%APPDATA%\Claude\logs\`
- Claude Code: `claude --debug` shows MCP startup output in the terminal
