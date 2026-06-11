"""
Tools module for EasyPanel MCP Server.

Provides modular tools for managing EasyPanel resources using FastMCP.
"""

from src.tools.services import register_tools as register_services_tools
from src.tools.deployments import register_tools as register_deployments_tools
from src.tools.networks import register_tools as register_networks_tools
from src.tools.projects import register_tools as register_projects_tools
from mcp.server.fastmcp import FastMCP
from src.client import EasyPanelClient


def register_all_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register all modular tools in the FastMCP instance.
    
    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """
    register_services_tools(mcp, client)
    register_deployments_tools(mcp, client)
    register_networks_tools(mcp, client)
    register_projects_tools(mcp, client)


__all__ = [
    "register_all_tools",
    "register_services_tools",
    "register_deployments_tools",
    "register_networks_tools",
    "register_projects_tools"
]
