"""Expense Tracker MCP server (FastMCP).

This module exposes Model Context Protocol (MCP) tools and a resource for
tracking personal expenses in a local SQLite database next to this file.

Step 1 — Dependencies
    Install from the project root (``uv sync`` or ``pip install -e .``).
    Requires Python 3.13+ and ``fastmcp`` (see ``pyproject.toml``).

Step 2 — Optional categories file
    The URI ``expense://categories`` reads ``categories.json`` beside ``main.py``.
    Create that file (JSON) if you want the resource to succeed; otherwise only
    the tools are usable.

Step 3 — Database
    ``expenses.db`` is created automatically on first import in the same
    directory as ``main.py``. Schema: ``id``, ``date`` (ISO ``YYYY-MM-DD`` text),
    ``amount``, ``category``, ``subcategory``, ``note``.

Step 4 — Run the server
    From the project root::

        uv run python main.py

    Or use FastMCP development tooling (e.g. ``fastmcp dev``) per your setup.

Date convention
    Store and query dates as strings in ``YYYY-MM-DD`` form so ``BETWEEN``
    comparisons in SQLite behave chronologically.
"""

from __future__ import annotations

import json
import os
import random
import sqlite3

from fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")


def init_db() -> None:
    """Ensure the expenses table exists in ``DB_PATH`` (creates file if needed).

    Called once at module load. Safe to call repeatedly (``IF NOT EXISTS``).
    """
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)


init_db()


@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
) -> dict[str, str | int | None]:
    """Insert one expense row and return the new row id.

    Args:
        date: Calendar date of the expense, preferably ``YYYY-MM-DD``.
        amount: Monetary amount (positive number).
        category: High-level label (e.g. food, transport).
        subcategory: Optional finer grouping (default empty string).
        note: Optional free text (default empty string).

    Returns:
        A dict with ``status`` ``"ok"`` and ``id`` set to the new SQLite
        ``INTEGER PRIMARY KEY``, or ``None`` if the driver does not expose it.
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses(start_date: str, end_date: str) -> list[dict[str, str | float | int]]:
    """Return all expenses with ``date`` between ``start_date`` and ``end_date``, inclusive.

    Rows are ordered by ``id`` ascending.

    Args:
        start_date: Range start, ``YYYY-MM-DD`` recommended.
        end_date: Range end, ``YYYY-MM-DD`` recommended.

    Returns:
        List of dicts with keys ``id``, ``date``, ``amount``, ``category``,
        ``subcategory``, ``note``.
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None,
) -> list[dict[str, str | float]]:
    """Aggregate total spend per category over a date range.

    Args:
        start_date: Range start, ``YYYY-MM-DD`` recommended.
        end_date: Range end, ``YYYY-MM-DD`` recommended.
        category: If set, only this category is included in the aggregation.

    Returns:
        List of dicts with keys ``category`` and ``total_amount`` (sum of
        ``amount``). Sorted by ``category`` ascending.
    """
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """
        params: list[str] = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.resource("expense://categories", mime_type="application/json")
def categories() -> str:
    """MCP resource: raw contents of ``categories.json`` beside ``main.py``.

    The file is read on each request so edits apply without restarting the
    server. Returns UTF-8 text; MIME type is ``application/json``.

    Raises:
        FileNotFoundError: If ``categories.json`` does not exist.
    """
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

# Resource: Server Information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about the server"""
    info = {
        "name": "Remote Expense MCP",
        "version": "1.0.0",
        "description": "A MCP server for remote expense workflows",
        "author": "Mayank Chugh",
        "author_email": "remote-expense@example.com",
        "url": "https://github.com/remote-expense/remote-expense-mcp",
        "license": "MIT",
        "copyright": "Copyright 2026 Remote Expense",
        "copyright_year": 2026,
        "copyright_owner": "Remote Expense",
        "copyright_owner_email": "remote-expense@example.com",
        "tools": ["add", "random_number"],
    }
    return json.dumps(info, indent=2)

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)