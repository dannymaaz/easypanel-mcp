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

from mcp.server import MCPServer

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
async def lifespan(server: MCPServer) -> AsyncIterator[None]:
    """Manage the EasyPanel connection lifecycle."""
    logger.info("Starting EasyPanel MCP Server...")
    await client.connect()
    logger.info("Connected to EasyPanel at %s", config.easypanel.base_url)
    try:
        yield
    finally:
        logger.info("Shutting down EasyPanel MCP Server...")
        await client.disconnect()
        logger.info("Server shutdown complete")


# MCP SDK v2 keeps server identity/lifecycle configuration in the constructor.
# Transport-specific settings such as host and port are passed to run().
mcp = MCPServer(
    "easypanel-mcp",
    instructions="Exposes EasyPanel infrastructure management tools to AI agents.",
    lifespan=lifespan,
)

# Register all modular tools
register_all_tools(mcp, client)


def resolve_transport(transport_arg: str) -> str:
    """Normalize CLI transport aliases to MCP SDK v2 transport names."""
    normalized = transport_arg.strip().lower()
    if normalized in {"http", "streamable-http", "streamable_http"}:
        return "streamable-http"
    if normalized == "sse":
        return "sse"
    return "stdio"


def main() -> None:
    """Main entry point."""
    # stdio is the default for local MCP clients. `http` now selects the modern
    # Streamable HTTP transport; legacy SSE remains available explicitly.
    transport_arg = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    transport = resolve_transport(transport_arg)

    logger.info("Running MCP server using '%s' transport", transport)

    if transport == "streamable-http":
        logger.info(
            "Streamable HTTP server listening on %s:%s/mcp",
            config.server.host,
            config.server.port,
        )
        mcp.run(
            transport="streamable-http",
            host=config.server.host,
            port=config.server.port,
            streamable_http_path="/mcp",
            stateless_http=True,
        )
    elif transport == "sse":
        logger.info("SSE server listening on %s:%s", config.server.host, config.server.port)
        mcp.run(
            transport="sse",
            host=config.server.host,
            port=config.server.port,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
