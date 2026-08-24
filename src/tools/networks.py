"""
Networks Tool Module.

Provides tools for managing EasyPanel networks using MCPServer.
"""

import logging
from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: MCPServer, client: EasyPanelClient) -> None:
    """
    Register networks tools on the MCPServer instance.

    Args:
        mcp: MCPServer instance
        client: EasyPanel API client
    """

    @mcp.tool(
        name="list_networks",
        annotations=ToolAnnotations(read_only_hint=True),
    )
    async def list_networks() -> dict[str, Any]:
        """
        Analyze network topology in EasyPanel.

        Note: EasyPanel manages Docker networks automatically and does not expose
        them via the tRPC API, so this infers a per-project topology (internal vs
        public services) from the services' port configuration.
        """
        networks = await client.list_networks()
        return {
            "success": True,
            "data": networks,
            "message": f"Found {len(networks)} networks"
        }

    @mcp.tool(
        name="create_network",
        annotations=ToolAnnotations(read_only_hint=True),
    )
    async def create_network(
        name: str,
        internal: bool = False,
        driver: str = "overlay"
    ) -> dict[str, Any]:
        """
        Advisory helper for network creation.

        IMPORTANT: EasyPanel creates and manages Docker networks automatically
        when services are deployed; there is no API to create one directly. This
        tool does NOT create anything — it returns guidance. To isolate services,
        set internal=true when creating the service instead.

        Args:
            name: Network name
            internal: Whether the network is internal (isolated from internet)
            driver: Network driver (overlay, bridge, etc.)
        """
        network = await client.create_network(
            name=name,
            internal=internal,
            driver=driver
        )
        network_type = "internal (isolated)" if internal else "public"
        return {
            "success": True,
            "data": network,
            "message": f"Network '{name}' created as {network_type} network"
        }

    @mcp.tool(
        name="delete_network",
        annotations=ToolAnnotations(read_only_hint=True),
    )
    async def delete_network(network_id: str) -> dict[str, Any]:
        """
        Advisory helper for network deletion.

        IMPORTANT: EasyPanel removes a network automatically once all services in
        it are deleted; there is no API to delete one directly. This tool does NOT
        delete anything — it returns guidance.

        Args:
            network_id: Network ID
        """
        result = await client.delete_network(network_id)
        return {
            "success": True,
            "data": result,
            "message": f"Network {network_id} deleted successfully"
        }
