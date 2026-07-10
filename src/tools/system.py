"""
System & Monitoring Tool Module.

Exposes monitoring, health and domain helpers that already exist on the
EasyPanelClient but were not previously surfaced as MCP tools.
"""

import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register system / monitoring / domain tools on the FastMCP instance.

    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """

    @mcp.tool(
        name="get_system_stats",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_system_stats() -> dict[str, Any]:
        """Get host system statistics (CPU, memory, disk, uptime)."""
        stats = await client.get_system_stats()
        return {
            "success": True,
            "data": stats,
            "message": "System statistics retrieved"
        }

    @mcp.tool(
        name="get_service_stats",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_service_stats() -> dict[str, Any]:
        """Get per-service runtime statistics."""
        stats = await client.get_service_stats()
        return {
            "success": True,
            "data": stats,
            "message": "Service statistics retrieved"
        }

    @mcp.tool(
        name="health_check",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def health_check() -> dict[str, Any]:
        """Check whether the EasyPanel API is reachable and the session is valid."""
        healthy = await client.health_check()
        return {
            "success": True,
            "data": {"healthy": healthy},
            "message": "EasyPanel API is healthy" if healthy else "EasyPanel API is NOT reachable"
        }

    @mcp.tool(
        name="get_server_ip",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_server_ip() -> dict[str, Any]:
        """Get the server's public IP address."""
        ip = await client.get_server_ip()
        return {
            "success": True,
            "data": {"ip": ip},
            "message": f"Server IP: {ip}" if ip else "Server IP not available"
        }

    @mcp.tool(
        name="list_domains",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_domains(service_id: Optional[str] = None) -> dict[str, Any]:
        """
        List domains, optionally filtered by service.

        Args:
            service_id: Optional service ID to filter domains
        """
        domains = await client.list_domains(service_id)
        return {
            "success": True,
            "data": domains,
            "message": f"Found {len(domains)} domains"
        }

    @mcp.tool(name="create_domain")
    async def create_domain(name: str, service_id: Optional[str] = None) -> dict[str, Any]:
        """
        Create a new domain, optionally bound to a service.

        Args:
            name: Domain name (e.g. app.example.com)
            service_id: Optional service ID to attach the domain to
        """
        domain = await client.create_domain(name=name, service_id=service_id)
        return {
            "success": True,
            "data": domain,
            "message": f"Domain '{name}' created successfully"
        }
