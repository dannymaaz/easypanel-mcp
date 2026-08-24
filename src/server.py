"""
EasyPanel MCP Server.

Main server implementation using the official Model Context Protocol (MCP) SDK.
Provides AI agents with tools to manage EasyPanel infrastructure.
"""

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

# When this file is executed directly (for example by an MCP client using an
# absolute path to src/server.py), Python only adds the src/ directory to
# sys.path. Add the repository root so project-local imports keep working no
# matter which working directory the client launches from.
if __package__ in (None, ""):
    repository_root = str(Path(__file__).resolve().parents[1])
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)

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


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[None]:
    """
    Manage the EasyPanel connection lifecycle.

    FastMCP no longer exposes @on_startup/@on_shutdown decorators; the supported
    way to run startup/shutdown logic is a lifespan async context manager passed
    to the FastMCP constructor.
    """
    logger.info("Starting EasyPanel MCP Server...")
    await client.connect()
    logger.info("Connected to EasyPanel at %s", config.easypanel.base_url)
    try:
        yield
    finally:
        logger.info("Shutting down EasyPanel MCP Server...")
        await client.disconnect()
        logger.info("Server shutdown complete")


# Initialize FastMCP Server.
# Note: current FastMCP takes `instructions` (not `title`/`description`) and the
# lifespan context manager. host/port are settings used by the SSE transport.
mcp = FastMCP(
    "easypanel-mcp",
    instructions="Exposes EasyPanel infrastructure management tools to AI agents.",
    lifespan=lifespan,
    host=config.server.host,
    port=config.server.port,
)

# Register all modular tools
register_all_tools(mcp, client)


def main() -> None:
    """Main entry point."""
    # Determine transport mode (stdio or sse)
    # stdio is default for local execution (e.g. Claude Desktop)
    transport_arg = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    # Map "http" argument to "sse" (Server-Sent Events) supported by FastMCP
    transport = "sse" if transport_arg in ("http", "sse") else "stdio"

    logger.info("Running MCP server using '%s' transport", transport)

    if transport == "sse":
        logger.info("SSE server listening on %s:%s", config.server.host, config.server.port)
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
