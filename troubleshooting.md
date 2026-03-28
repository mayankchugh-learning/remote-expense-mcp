# Troubleshooting

This guide covers common problems when running **remote-expense-mcp** locally, in the FastMCP inspector, or from an MCP client.

## Resource errors in the inspector (e.g. `info://server`)

### `MCP error 0: ... name 'name' is not defined` (or similar `NameError`)

**Cause:** In Python, dictionary keys must be strings when you intend a literal key. Writing `name: "value"` uses the variable `name` as the key, not the string `"name"`.

**Fix:** Use quoted keys, for example `"name": "Remote Expense MCP"`, not `name: "Remote Expense MCP"`.

### `TypeError: Object of type ... is not JSON serializable`

**Cause:** `json.dumps()` cannot serialize arbitrary objects (for example function references, custom classes, or `datetime` without a default handler).

**Fix:** Pass only JSON-safe types (`str`, `int`, `float`, `bool`, `list`, `dict`, or `None`). For tools, list their names as strings (for example `["add", "random_number"]`) instead of passing function objects.

### Resource still shows an old error after editing code

**Fix:** Restart the server process. The FastMCP dev inspector and `uv run main.py` both load `main.py` when they start; a refresh button in the UI may not reload Python code.

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

**Cause:** Another process is bound to the same host and port (by default `main.py` uses HTTP on port **8000**).

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
3. Confirm the entrypoint matches how you run the server (`fastmcp run ...`, or `main.py`, or a future `fastmcp.json`).

### HTTP transport

**Symptoms:** Browser or remote client cannot reach the server.

**Fix:**

1. Confirm the host and port match (`0.0.0.0` listens on all interfaces; some clients require `127.0.0.1` or your machine’s LAN IP).
2. Check local firewalls or VPN rules blocking the port.

---

## FastMCP inspector / `fastmcp dev`

**Symptoms:** Tools or resources do not appear, or errors only in the inspector.

**Fix:**

1. Run commands from the **repository root** so imports and relative paths resolve.
2. Pass the correct module file (e.g. `main.py`) to `fastmcp dev inspector`.
3. After changing code, restart the dev server if behavior does not update.

---

## Getting more detail

1. Run the server in a terminal and watch stderr when a client invokes a tool or resource.
2. Re-run a minimal Python check against your handlers (for example importing `main` and calling small functions that mirror tool logic).
3. Confirm `uv run fastmcp version` reports expected versions when investigating FastMCP-specific behavior.
