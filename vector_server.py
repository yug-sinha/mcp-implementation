"""
MCP Vector Search Server

This server exposes an MCP tool named 'vector_search' to simulate a vector database query.
In production, this tool would query a real vector database. Here, it returns a hard-coded result.
The server uses STDIO transport and is intended for an MCP host (e.g., Claude for Desktop).

Run this server using:
    uv run vector_server.py
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
logger = logging.getLogger("VectorSearchServer")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Starting MCP Vector Search Server...")

# Create a FastMCP server instance with the name "VectorSearch"
mcp = FastMCP("VectorSearch")

@mcp.tool("vector_search")
def vector_search_tool(params):
    """
    Simulate a vector database query.

    Args:
        params (dict): Should include a key "query" containing a natural language query.

    Returns:
        dict: A dictionary with simulated vector search results and echoes the query.
    """
    logger.debug(f"Received parameters for vector_search_tool: {params}")
    query = params.get("query", "")
    results = [
        {"doc_id": 1, "score": 0.95},
        {"doc_id": 2, "score": 0.90}
    ]
    logger.debug(f"Simulated vector search results: {results}")
    return {"results": results, "query": query}

if __name__ == '__main__':
    logger.info("Running VectorSearch server with STDIO transport...")
    mcp.run(transport='stdio')
