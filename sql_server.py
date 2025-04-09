"""
MCP SQL Warehouse Server

This server exposes an MCP tool named 'txt_to_sql' to simulate converting a plain-text
instruction into an SQL query for a warehouse. In production, you might replace the simulated
conversion with an actual NLP module. The server uses STDIO transport and is intended for use
with an MCP host (e.g., Claude for Desktop).

Run this server using:
    uv run sql_server.py
or directly with Python.
"""

import logging
from colorlog import ColoredFormatter
from mcp.server.fastmcp import FastMCP

# Setup colored logging for the server.
LOGFORMAT = "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s"
formatter = ColoredFormatter(LOGFORMAT, log_colors={
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
})
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("SQLWarehouseServer")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Starting MCP SQL Warehouse Server...")

# Create a FastMCP server instance with the name "SQLWarehouse"
mcp = FastMCP("SQLWarehouse")

@mcp.tool("txt_to_sql")
def txt_to_sql_tool(params):
    """
    Convert a textual instruction to a simulated SQL query.

    Args:
        params (dict): Should include a key "text" containing a natural language instruction.

    Returns:
        dict: A dictionary with the simulated SQL query under the key "sql_query".
    """
    logger.debug(f"Received parameters for txt_to_sql_tool: {params}")
    text = params.get("text", "")
    sql_query = f"SELECT * FROM warehouse WHERE description LIKE '%{text}%';"
    logger.debug(f"Generated SQL query: {sql_query}")
    return {"sql_query": sql_query}

if __name__ == '__main__':
    logger.info("Running SQLWarehouse server with STDIO transport...")
    mcp.run(transport='stdio')
