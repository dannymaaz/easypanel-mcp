"""
Networks Tool Module.

Provides tools for managing EasyPanel networks using the FastMCP registration style.
"""

import logging
from typing import Any
from mcp.server.fastmcp import FastMCP
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register networks tools on the FastMCP instance.
    
    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """
    
    @mcp.tool(name="list_networks")
    async def list_networks() -> dict[str, Any]:
        """
        List all networks in EasyPanel.
        """
        networks = await client.list_networks()
        return {
            "success": True,
            "data": networks,
            "message": f"Found {len(networks)} networks"
        }
    
    @mcp.tool(name="create_network")
    async def create_network(
        name: str,
        internal: bool = False,
        driver: str = "overlay"
    ) -> dict[str, Any]:
        """
        Create a new network in EasyPanel. Use internal=true for isolated networks.
        
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
    
    @mcp.tool(name="delete_network")
    async def delete_network(network_id: str) -> dict[str, Any]:
        """
        Delete a network from EasyPanel.
        
        Args:
            network_id: Network ID
        """
        result = await client.delete_network(network_id)
        return {
            "success": True,
            "data": result,
            "message": f"Network {network_id} deleted successfully"
        }
