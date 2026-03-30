# Troubleshooting

This guide covers common problems when running **remote-expense-mcp** locally, in the FastMCP inspector, or from an MCP client (including Claude Desktop on Windows).

## Resolved issues (quick reference)

These problems were diagnosed and fixed while working on this codebase and related MCP setups. Use the links to jump to details.

| What went wrong | Typical symptom | Where to read |
|-----------------|-----------------|---------------|
| Dict keys written without quotes | `MCP error ... name 'name' is not defined` | [Resource errors](#resource-errors-in-the-inspector-eg-infoserver) |
| Non-JSON values in `json.dumps` | `TypeError: ... not JSON serializable` | [Resource errors](#resource-errors-in-the-inspector-eg-infoserver) |
| `from __future__` after normal imports | `SyntaxError: from __future__ imports must occur at the beginning of the file` | [`__future__` import order](#python-future-imports-must-come-first) |
| Inspector default reload | Node `Error: Not connected` / `sse.js` | [FastMCP inspector](#fastmcp-inspector--fastmcp-dev) |
| Wrong or placeholder `uv` path in Claude config | `spawn ... uv.exe ENOENT` | [Claude: ENOENT](#claude-desktop-windows-spawn-uvenv-enoent) |
| `uv run` without project context from Claude | `Failed to spawn: fastmcp` / `program not found` | [Claude: uv project directory](#claude-desktop-uv-run-and-project-directory) |
| Relative `main.py` when `cwd` is ignored | `can't open file 'C:\\Windows\\System32\\main.py'` | [Claude: uv project directory](#claude-desktop-uv-run-and-project-directory) |

---

## Resource errors in the inspector (e.g. `info://server`)

### `MCP error 0: ... name 'name' is not defined` (or similar `NameError`)

**Cause:** In Python, dictionary keys must be strings when you intend a literal key. Writing `name: "value"` uses the variable `name` as the key, not the string `"name"`.

**Fix:** Use quoted keys, for example `"name": "Remote Expense MCP"`, not `name: "Remote Expense MCP"`.

### `TypeError: Object of type ... is not JSON serializable`

**Cause:** `json.dumps()` cannot serialize arbitrary objects (for example function references, custom classes, or `datetime` without a default handler).

**Fix:** Pass only JSON-safe types (`str`, `int`, `float`, `bool`, `list`, `dict`, or `None`). For tools, list their names as strings (for example `["add_expense", "list_expenses", "summarize"]`) instead of passing function objects.

### Resource still shows an old error after editing code

**Fix:** Restart the server process. The FastMCP dev inspector and `uv run main.py` both load `main.py` when they start; a refresh button in the UI may not reload Python code.

---

## Python: `from __future__` imports must come first

**Symptom:** Importing the server module or running `fastmcp dev inspector` fails with:

`SyntaxError: from __future__ imports must occur at the beginning of the file`

**Cause:** Only a **module docstring**, comments, and other future-imports may appear before `from __future__ import annotations`. Any normal import (`import json`, etc.) before that line triggers this error.

**Fix:**

1. Put the module docstring first (if you use one).
2. Put `from __future__ import annotations` immediately after it.
3. Put all other imports after that block.

---

## Tools fail with `NameError` or missing imports

**Symptoms:** A tool runs in the client but errors with `name 'X' is not defined` or `NameError`.

**Fix:**

1. Open `main.py` and confirm every name used in a tool or resource is either defined in that file or imported at the top (for example `import random` for `random.randint`).
2. From the repo root, run a quick import check:

   ```powershell
   uv run python -c "import main; print('ok')"
   ```

---

## `uv` or dependencies

### `uv: command not found` (or not recognized)

**Fix:** Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and ensure it is on your `PATH`. On Windows PowerShell, the installer snippet is shown in [README.md](README.md).

### Packages out of date or lockfile mismatch

**Fix:** From the repository root:

```bash
uv sync
```

---

## Port already in use (`Address already in use`)

**Cause:** Another process is bound to the same host and port (by default `main.py` may use HTTP on port **8000**).

**Fix:**

1. Stop the other process, or change the port in `mcp.run(..., port=...)` in `main.py`.
2. On Windows, you can inspect listeners (example PowerShell): `Get-NetTCPConnection -LocalPort 8000` (may require elevation depending on the system).

---

## MCP client cannot connect to the server

### Stdio / `uv run` configuration

**Symptoms:** Client shows “server failed to start” or timeouts.

**Fix:**

1. Set `cwd` in the client config to the **absolute path** of this repository (see [README.md](README.md) for an example).
2. Use the same interpreter path the project expects: prefer `uv` with `args` like `["run", ...]` so dependencies resolve from `pyproject.toml` / `uv.lock`.
3. Confirm the entrypoint matches how you run the server (`fastmcp run ...`, or `main.py`, or a `fastmcp.json`).
4. If the host app starts the process with a working directory like `C:\Windows\System32`, pass **`uv run --directory <absolute project path>`** in `args` so `uv` discovers `pyproject.toml` and the project environment even when `cwd` is wrong (see [Claude Desktop](#claude-desktop-uv-run-and-project-directory)).

### HTTP transport

**Symptoms:** Browser or remote client cannot reach the server.

**Fix:**

1. Confirm the host and port match (`0.0.0.0` listens on all interfaces; some clients require `127.0.0.1` or your machine’s LAN IP).
2. Check local firewalls or VPN rules blocking the port.

---

## FastMCP inspector / `fastmcp dev`

### Node.js: `Error: Not connected` (often `sse.js` in the stack trace)

**Symptoms:** The MCP Inspector crashes in Node after a request, with something like `Error: Not connected` from `@modelcontextprotocol/sdk` (for example `sse.js`).

**Cause:** `fastmcp dev inspector` turns on **`--reload` by default**. Reload restarts the Python stdio server when files change; the inspector’s SSE bridge can lose session state and throw this error (similar constraints are documented in FastMCP for reload + SSE).

**Fix:** Run the inspector **without** auto-reload:

```powershell
uv run fastmcp dev inspector main.py --no-reload
```

After you edit `main.py`, stop the inspector (Ctrl+C) and start it again, or temporarily omit `--no-reload` only while debugging reload behavior.

### Other inspector issues

**Symptoms:** Tools or resources do not appear, or errors only in the inspector.

**Fix:**

1. Run commands from the **repository root** so imports and relative paths resolve.
2. Pass the correct module file (e.g. `main.py`) to `fastmcp dev inspector`.
3. After changing code, restart the dev server if behavior does not update.

---

## Claude Desktop (Windows): `spawn ... uv.exe` ENOENT

**Symptoms:** A notification like `MCP <name>: spawn` with a path ending in `uv.exe` and **ENOENT**, or `mcp-server-*.log` shows `spawn C:\...\uv.exe ENOENT`.

**Cause:** The `command` for that server points at a path that does not exist. Common cases:

- A **placeholder username** was copied from docs (for example `C:\Users\you\...`) instead of your real profile folder.
- `uv` was installed to a different location than `AppData\Local\Programs\uv` (for example the standalone installer often uses **`%USERPROFILE%\.local\bin\uv.exe`**).

**Fix:**

1. In PowerShell, find the real executable:

   ```powershell
   where.exe uv
   ```

2. Set **`command`** in `claude_desktop_config.json` to that **full path** (with doubled backslashes in JSON, e.g. `C:\\Users\\YourName\\.local\\bin\\uv.exe`).
3. Ensure **`cwd`** is the project directory that contains `main.py` (or your server entrypoint), and prefer the **`uv run --directory`** pattern below so it still works if `cwd` is ignored.
4. Fully quit and restart **Claude** so it reloads the config. Logs for a single server live next to the config, for example under:

   `%LocalAppData%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\logs\`

**Note:** Using the bare command `"uv"` only works if Claude’s spawned environment includes the folder that contains `uv.exe` on `PATH`; a **full path** is more reliable for desktop apps.

---

## Claude Desktop: `uv run` and project directory

**Symptoms:**

- Log line: `error: Failed to spawn: fastmcp` with **`Caused by: program not found`**.
- Or Python: `can't open file 'C:\\Windows\\System32\\main.py'` (or another wrong directory).

**Cause:**

1. **`uv run fastmcp ...` without a discovered project:** If the process starts with cwd somewhere like `System32`, `uv` may not find `pyproject.toml` / `.venv`, so the `fastmcp` script is not on the environment used for the child process.
2. **Relative `main.py`:** If the host does not honor `cwd`, `python main.py` resolves against the wrong folder.

**Fix:** Put the project path in **`uv`’s** arguments so discovery does not depend on the host’s cwd. Example for a server whose repo is `C:\githunb\Claude\proxy-mcp-server`:

```json
"proxy-mcp-server": {
  "command": "C:\\Users\\YOURNAME\\.local\\bin\\uv.exe",
  "args": [
    "run",
    "--directory",
    "C:\\githunb\\Claude\\proxy-mcp-server",
    "fastmcp",
    "run",
    "C:\\githunb\\Claude\\proxy-mcp-server\\main.py"
  ]
}
```

Replace `YOURNAME` with your Windows username (use the path from `where.exe uv`). **Doubled backslashes** are required in JSON.

`uv run --directory ...` changes into that folder before running, so `python-dotenv` and paths relative to the project behave consistently.

**Related:** If the server requires secrets (for example `FASTMCP_REMOTE_TOKEN`), add them under `env` in the same JSON block, or keep a `.env` in that project directory (loaded after cwd is correct).

---

## Getting more detail

1. Run the server in a terminal and watch stderr when a client invokes a tool or resource.
2. Re-run a minimal Python check against your handlers (for example importing `main` and calling small functions that mirror tool logic).
3. Confirm `uv run fastmcp version` reports expected versions when investigating FastMCP-specific behavior.
4. For Claude Desktop, open the per-server log (`mcp-server-<name>.log`) under the Claude logs folder; errors often appear on stderr right after the `initialize` message.
