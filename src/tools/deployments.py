"""
Deployments Tool Module.

Provides tools for managing EasyPanel deployments using the FastMCP registration style.
"""

import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register deployments tools on the FastMCP instance.
    
    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """
    
    @mcp.tool(name="list_deployments")
    async def list_deployments(project_id: Optional[str] = None) -> dict[str, Any]:
        """
        List all deployments in EasyPanel, optionally filtered by project.
        
        Args:
            project_id: Optional project ID to filter deployments
        """
        deployments = await client.list_deployments(project_id)
        return {
            "success": True,
            "data": deployments,
            "message": f"Found {len(deployments)} deployments"
        }
    
    @mcp.tool(name="get_deployment")
    async def get_deployment(deployment_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific deployment.
        
        Args:
            deployment_id: Deployment ID
        """
        deployment = await client.get_deployment(deployment_id)
        return {
            "success": True,
            "data": deployment,
            "message": f"Deployment {deployment_id} retrieved"
        }
    
    @mcp.tool(name="create_deployment")
    async def create_deployment(
        project_id: str,
        service_id: str,
        image: str,
        config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Create a new deployment in EasyPanel.
        
        Args:
            project_id: Project ID
            service_id: Service ID
            image: Docker image to deploy
            config: Additional deployment configuration
        """
        deployment = await client.create_deployment(
            project_id=project_id,
            service_id=service_id,
            image=image,
            config=config
        )
        return {
            "success": True,
            "data": deployment,
            "message": f"Deployment created successfully for service {service_id}"
        }
    
    @mcp.tool(name="get_deployment_logs")
    async def get_deployment_logs(deployment_id: str) -> dict[str, Any]:
        """
        Get logs from a deployment.
        
        Args:
            deployment_id: Deployment ID
        """
        logs = await client.get_deployment_logs(deployment_id)
        return {
            "success": True,
            "data": logs,
            "message": f"Retrieved {len(logs)} log lines for deployment {deployment_id}"
        }
