# remote-expense-mcp

MCP (Model Context Protocol) server for remote expense workflows. This repository is scaffolded for tools and resources that help agents record, query, or reconcile expenses against a remote backend.

The Python stack uses [uv](https://docs.astral.sh/uv/) for environments and dependencies and [FastMCP](https://fastmcp.wiki/) to implement the MCP server.

## Prerequisites

- Python 3.10+ (uv can install a pinned version per project)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (see below)

## Install uv

If you already have Python, you can install uv with pip (often the quickest first step):

```bash
pip install uv
```

Use `python -m pip install uv` if `pip` is not on your `PATH`. For a user install without touching system Python: `pip install --user uv`.

Other options (standalone binary, often preferred for CI and machines without Python yet) are in the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/):

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS and Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirm `uv` is on your `PATH`, then check the version:

```bash
uv --version
```

## Initialize the project with uv

From the repository root, create a uv project. If `pyproject.toml` already exists, `uv init` will refuse to run; use `uv add` / `uv sync` instead, or edit `pyproject.toml` by hand.

**Repo already has docs and `.gitignore` (like this one):** add only a project file so you do not get a second README or starter layout you need to delete:

```bash
uv init --bare
```

Then set `name`, `requires-python`, and `dependencies` in `pyproject.toml` before running `uv sync`.

**Greenfield app** (new folder; gives `main.py`, `.python-version`, and default `readme` in metadata):

```bash
uv init --app
```

**Packaged app** (installable package with `src/` layout—handy for a CLI entrypoint or tests):

```bash
uv init --package --app
```

Match `[project].name` and related fields in `pyproject.toml` to this repository.

## Create a virtual environment

From the repository root:

```bash
uv venv
```

This creates `.venv` in the current directory. Activate it when you want a classic shell-bound venv (optional with uv; `uv run` uses the project environment automatically):

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS and Linux:**

```bash
source .venv/bin/activate
```

Install and lock project dependencies (after dependencies are listed in `pyproject.toml`):

```bash
uv sync
```

## FastMCP: add dependency and common tasks

Add FastMCP to the project:

```bash
uv add fastmcp
```

Verify the CLI and versions:

```bash
uv run fastmcp version
```

**Typical task-style commands** (run from the repo root; adjust file names to match your tree):

| Task | Command |
|------|---------|
| Install / refresh deps | `uv sync` |
| Add another runtime dependency | `uv add <package>` |
| Add a dev-only dependency | `uv add --dev <package>` |
| Check FastMCP / MCP versions | `uv run fastmcp version` |
| Run server from `fastmcp.json` | `uv run fastmcp run fastmcp.json` |
| Run server when `fastmcp.json` is in cwd | `uv run fastmcp run` |
| Run the server module directly | `uv run python -m remote_expense_mcp` *(after you add that package/module)* |

After you add a `fastmcp.json` (see [FastMCP server configuration](https://gofastmcp.com/deployment/server-configuration)), the `uv run fastmcp run` flow is the usual production-style entry.

For production, prefer pinning FastMCP to an exact version in `pyproject.toml` (see [FastMCP versioning](https://fastmcp.wiki/en/development/releases#versioning-policy)).

Optional: set `requires-python` and Python version for uv:

```bash
uv python pin 3.12
```

## Environment variables

When `.env.example` exists, copy it to `.env` and set API keys or service URLs. Keep secrets out of git (they are ignored via `.gitignore`).

## MCP client configuration

Point your MCP client at uv and FastMCP. Example (adjust `cwd` and config path):

```json
{
  "mcpServers": {
    "remote-expense": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "fastmcp.json"],
      "cwd": "C:\\githunb\\Claude\\remote-expense-mcp"
    }
  }
}
```

On macOS or Linux, set `cwd` to the absolute path of this repository.

## License

See [LICENSE](LICENSE).

fastmcp run main.py --transport http --host 0.0.0.0 --port 8000
or 
uv run main.py

uv run fastmcp dev inspector main.py --no-reload