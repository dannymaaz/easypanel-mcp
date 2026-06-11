"""
Services Tool Module.

Provides tools for managing EasyPanel services using the FastMCP registration style.
"""

import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register services tools on the FastMCP instance.
    
    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """
    
    @mcp.tool(name="list_services")
    async def list_services(project_id: Optional[str] = None) -> dict[str, Any]:
        """
        List all services in EasyPanel, optionally filtered by project.
        
        Args:
            project_id: Optional project ID to filter services
        """
        services = await client.list_services(project_id)
        return {
            "success": True,
            "data": services,
            "message": f"Found {len(services)} services"
        }
    
    @mcp.tool(name="get_service")
    async def get_service(service_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific service.
        
        Args:
            service_id: Service ID
        """
        service = await client.get_service(service_id)
        return {
            "success": True,
            "data": service,
            "message": f"Service {service_id} retrieved"
        }
    
    @mcp.tool(name="create_service")
    async def create_service(
        name: str,
        project_id: str,
        image: str,
        config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Create a new service in EasyPanel.
        
        Args:
            name: Service name
            project_id: Project ID
            image: Docker image (e.g., nginx:latest, postgres:15)
            config: Additional configuration (ports, env vars, volumes, etc.)
        """
        service = await client.create_service(
            name=name,
            project_id=project_id,
            image=image,
            config=config
        )
        return {
            "success": True,
            "data": service,
            "message": f"Service '{name}' created successfully"
        }
    
    @mcp.tool(name="update_service")
    async def update_service(service_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Update service configuration.
        
        Args:
            service_id: Service ID
            config: New configuration settings
        """
        service = await client.update_service(service_id, config)
        return {
            "success": True,
            "data": service,
            "message": f"Service {service_id} updated successfully"
        }
    
    @mcp.tool(name="delete_service")
    async def delete_service(service_id: str) -> dict[str, Any]:
        """
        Delete a service from EasyPanel.
        
        Args:
            service_id: Service ID
        """
        result = await client.delete_service(service_id)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} deleted successfully"
        }
    
    @mcp.tool(name="restart_service")
    async def restart_service(service_id: str) -> dict[str, Any]:
        """
        Restart a service.
        
        Args:
            service_id: Service ID
        """
        result = await client.restart_service(service_id)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} restarted successfully"
        }
    
    @mcp.tool(name="get_service_logs")
    async def get_service_logs(service_id: str, lines: int = 100) -> dict[str, Any]:
        """
        Get logs from a service.
        
        Args:
            service_id: Service ID
            lines: Number of log lines to retrieve
        """
        logs = await client.get_service_logs(service_id, lines)
        return {
            "success": True,
            "data": logs,
            "message": f"Retrieved {len(logs)} log lines for service {service_id}"
        }
