"""
Projects Tool Module.

Provides tools for managing EasyPanel projects using the FastMCP registration style.
"""

import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register projects tools on the FastMCP instance.
    
    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """
    
    @mcp.tool(
        name="list_projects",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_projects() -> dict[str, Any]:
        """
        List all projects in EasyPanel.
        """
        projects = await client.list_projects()
        return {
            "success": True,
            "data": projects,
            "message": f"Found {len(projects)} projects"
        }
    
    @mcp.tool(
        name="get_project",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_project(project_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific project.
        
        Args:
            project_id: Project ID
        """
        project = await client.get_project(project_id)
        return {
            "success": True,
            "data": project,
            "message": f"Project {project_id} retrieved"
        }
    
    @mcp.tool(name="create_project")
    async def create_project(name: str, description: Optional[str] = None) -> dict[str, Any]:
        """
        Create a new project in EasyPanel.
        
        Args:
            name: Project name
            description: Project description
        """
        project = await client.create_project(
            name=name,
            description=description
        )
        return {
            "success": True,
            "data": project,
            "message": f"Project '{name}' created successfully"
        }
    
    @mcp.tool(
        name="delete_project",
        annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True),
    )
    async def delete_project(project_id: str) -> dict[str, Any]:
        """
        Delete a project from EasyPanel, including all its services.
        This is destructive and cannot be undone.

        Args:
            project_id: Project ID
        """
        result = await client.delete_project(project_id)
        return {
            "success": True,
            "data": result,
            "message": f"Project {project_id} deleted successfully"
        }
