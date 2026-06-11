"""
EasyPanel MCP Server.

Main server implementation using the official Model Context Protocol (MCP) SDK.
Provides AI agents with tools to manage EasyPanel infrastructure.
"""

import asyncio
import logging
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP
from config import config
from src.client import EasyPanelClient
from src.tools import register_all_tools

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Validate configuration on startup
config.validate()

# Initialize EasyPanel client
client = EasyPanelClient(config.easypanel)

# Initialize FastMCP Server
mcp = FastMCP(
    "easypanel-mcp",
    title="EasyPanel MCP Server",
    description="Exposes EasyPanel management tools to AI agents"
)

# Register all modular tools
register_all_tools(mcp, client)


@mcp.on_startup()
async def startup() -> None:
    """Connect to EasyPanel API on server startup."""
    logger.info("Starting EasyPanel MCP Server...")
    await client.connect()
    logger.info("Server started successfully and connected to EasyPanel")


@mcp.on_shutdown()
async def shutdown() -> None:
    """Disconnect from EasyPanel API on server shutdown."""
    logger.info("Shutting down EasyPanel MCP Server...")
    await client.disconnect()
    logger.info("Server shutdown complete")


def main() -> None:
    """Main entry point."""
    # Determine transport mode (stdio or sse)
    # stdio is default for local execution (e.g. Claude Desktop)
    transport_arg = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    # Map "http" argument to "sse" (Server-Sent Events) supported by FastMCP
    transport = "sse" if transport_arg in ("http", "sse") else "stdio"
    
    logger.info(f"Running MCP server using '{transport}' transport")
    
    if transport == "sse":
        logger.info(f"SSE Server listening on {config.server.host}:{config.server.port}")
        mcp.run(
            transport="sse",
            host=config.server.host,
            port=config.server.port
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
