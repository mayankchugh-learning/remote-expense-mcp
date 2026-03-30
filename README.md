# remote-expense-mcp

MCP (Model Context Protocol) server built with [FastMCP](https://fastmcp.wiki/) for tracking personal expenses in a local SQLite database.

The Python stack uses [uv](https://docs.astral.sh/uv/) for environments and dependencies. The server lives in a single module, [`main.py`](main.py).

## What it exposes

| Kind | Name | Purpose |
|------|------|--------|
| Tool | `add_expense` | Insert a row (`date`, `amount`, `category`, optional `subcategory`, `note`) |
| Tool | `list_expenses` | Rows in an inclusive `start_date`–`end_date` range (`YYYY-MM-DD`) |
| Tool | `summarize` | Per-category totals and counts in a date range; optional `category` filter |
| Resource | `expense:///categories` | JSON list of categories (from `categories.json` beside `main.py`, or built-in defaults) |

Dates should be ISO strings `YYYY-MM-DD` so range queries sort correctly in SQLite.

## Storage

- **Database:** SQLite file `expenses.db` under the system temporary directory (see the log line `Database path: ...` when the server starts). This avoids read-only filesystem issues in some environments.
- **Optional file:** [`categories.json`](categories.json) next to `main.py` overrides the default category list for the resource; if it is missing, the server uses embedded defaults.

## Prerequisites

- Python **3.13+** ([`pyproject.toml`](pyproject.toml) sets `requires-python = ">=3.13"`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Install uv

If you already have Python:

```bash
pip install uv
```

Use `python -m pip install uv` if `pip` is not on your `PATH`.

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Other install options are in the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

**macOS and Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirm `uv` is on your `PATH`:

```bash
uv --version
```

## Project setup

From the repository root:

```bash
uv sync
```

This creates or refreshes `.venv` and installs `fastmcp` and `aiosqlite` per `pyproject.toml`.

Optional virtualenv activation (not required when using `uv run`):

**Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`  
**macOS / Linux:** `source .venv/bin/activate`

Verify FastMCP:

```bash
uv run fastmcp version
```

## Run the server

As checked in, [`main.py`](main.py) starts an **HTTP** MCP server on **all interfaces**, port **8000**:

```bash
uv run python main.py
```

Point HTTP-capable MCP clients at the URL your FastMCP version documents for this transport (see [FastMCP deployment / server configuration](https://gofastmcp.com/deployment/server-configuration)).

If your client expects **stdio** (subprocess + JSON-RPC on stdin/stdout), change the `if __name__ == "__main__"` block at the bottom of `main.py` to call `mcp.run()` with the default transport instead of `transport="http"`, then run the same command; configure the client to launch `uv` with `args` like `["run", "python", "main.py"]` and `cwd` set to this repo.

**FastMCP inspector / dev** (optional; adjust flags to match your FastMCP version):

```bash
uv run fastmcp dev inspector main.py --no-reload
```

## Typical uv commands

| Task | Command |
|------|---------|
| Install / refresh deps | `uv sync` |
| Add a dependency | `uv add <package>` |
| Add a dev dependency | `uv add --dev <package>` |
| Check FastMCP version | `uv run fastmcp version` |
| Run this server (HTTP) | `uv run python main.py` |

For production, pin exact versions in `pyproject.toml` ([FastMCP versioning](https://fastmcp.wiki/en/development/releases#versioning-policy)).

Optional Python pin for uv:

```bash
uv python pin 3.13
```

## MCP client configuration (stdio example)

After switching `main.py` to stdio if needed, example **Claude Desktop / Cursor–style** config (fix `cwd` to your machine):

```json
{
  "mcpServers": {
    "remote-expense": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "C:\\githunb\\Claude\\remote-expense-mcp"
    }
  }
}
```

On macOS or Linux, set `cwd` to the absolute path of this repository. If the client supports only HTTP/SSE, use the server URL from your FastMCP docs instead of a subprocess.

## Environment variables

There is no checked-in `.env.example` yet. If you add API keys or URLs later, keep secrets out of git (see `.gitignore`) and document them here when relevant.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common errors (inspector reload, `uv` path on Windows, resource JSON, import order).

## License

See [LICENSE](LICENSE).
