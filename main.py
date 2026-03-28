import json
import random

from fastmcp import FastMCP

mcp = FastMCP("remote-expense-mcp")
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together
    Args:
        a: The first number to add
        b: The second number to add
    Returns:
        The sum of the two numbers
    """
    return a + b

@mcp.tool
def random_number(min_value: int, max_value: int) -> int:
    """Generate a random number wihtin a range  
    Args:
        min_value: The minimum value of the random number
        max_value: The maximum value of the random number
    Returns:
        A random number between the two values

    """
    return random.randint(min_value, max_value)

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