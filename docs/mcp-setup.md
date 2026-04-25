# MCP Setup

Wire the `brain-mcp` server into Claude clients so they can call `brain_write`
and `brain_query` as tools.

## Design choices (deterministic by construction)

- **One DB per workspace**, addressed by absolute path
- **Absolute path to the venv binary** — never rely on `PATH`
- **`BRAIN_DB_PATH` env var** is the only way the server learns which DB to use
- **No auto-discovery, no defaults that depend on cwd, no fallback paths**

If the binary isn't where the config says, the server fails fast. That's the
point.

---

## Prerequisites

```powershell
cd "C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain"
uv sync --extra dev
```

This produces two console scripts:

- CLI: `C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain\.venv\Scripts\brain.exe`
- MCP server: `C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain\.venv\Scripts\brain-mcp.exe`

## Initialize a database

Pick one absolute path and use it everywhere. Recommended:

```powershell
$env:BRAIN_DB_PATH = "C:\Users\agnivad\.knowledge-brain\knowledge.db"
& "C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain\.venv\Scripts\brain.exe" --db-path $env:BRAIN_DB_PATH init
```

The DB is just a file; back it up like any other file.

---

## Claude Code (this CLI)

Add the server to your **user** scope so every project can use it:

```powershell
claude mcp add knowledge-brain `
  --scope user `
  --env BRAIN_DB_PATH=C:\Users\agnivad\.knowledge-brain\knowledge.db `
  -- "C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain\.venv\Scripts\brain-mcp.exe"
```

For a project-scoped server (committed to the repo), use `--scope project`
and the config lands in `.mcp.json` in the project root.

Verify:

```powershell
claude mcp list
```

You should see `knowledge-brain` listed. Restart Claude Code; the tools
`brain_write` and `brain_query` will appear in the tool list.

---

## Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`. If the file doesn't exist,
create it with exactly this content. If it does, merge the `knowledge-brain`
entry into the existing `mcpServers` object — leave other servers alone.

```json
{
  "mcpServers": {
    "knowledge-brain": {
      "command": "C:\\Users\\agnivad\\OneDrive - Microsoft\\Agniva\\knowledge-brain\\.venv\\Scripts\\brain-mcp.exe",
      "env": {
        "BRAIN_DB_PATH": "C:\\Users\\agnivad\\.knowledge-brain\\knowledge.db"
      }
    }
  }
}
```

Restart Claude Desktop. The hammer/tools icon in the chat input should show
`brain_write` and `brain_query`.

---

## Verify end-to-end

1. In a Claude session, ask: *"Use brain_write to store: Knowledge Brain MVP shipped on 2026-04-25. Tags: brain, milestone."*
2. Then: *"Use brain_query to look up 'milestone'."*

The query should return the just-written node. If it returns 0 results, the
two sessions are pointing at different DBs — double-check `BRAIN_DB_PATH` in
the config.

You can cross-check from the terminal:

```powershell
& "C:\Users\agnivad\OneDrive - Microsoft\Agniva\knowledge-brain\.venv\Scripts\brain.exe" `
  --db-path C:\Users\agnivad\.knowledge-brain\knowledge.db list --limit 5
```

The same node should appear in the JSON output.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Tool list empty after restart | Wrong path to `brain-mcp.exe` | Run the absolute path manually; if it errors, fix the path in the config |
| Server starts but `brain_query` returns nothing | Different DB than CLI | Make `BRAIN_DB_PATH` absolute and identical in every place |
| `mcp` import error in client log | venv broken | Re-run `uv sync --extra dev` in the repo root |
| `error: data_store/knowledge.db already exists` | Default DB conflict | Always pass `--db-path` explicitly; never rely on cwd |

The MCP client launches `brain-mcp.exe` as a subprocess and talks to it over
stdio. If the process can't start, the client logs the error. On Windows the
log location depends on the client; for Claude Desktop check
`%APPDATA%\Claude\logs\`.
