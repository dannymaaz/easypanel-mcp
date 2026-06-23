"""
Services Tool Module.

Provides tools for managing EasyPanel services using the FastMCP registration style.
"""

import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from src.client import EasyPanelClient

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, client: EasyPanelClient) -> None:
    """
    Register services tools on the FastMCP instance.

    Args:
        mcp: FastMCP server instance
        client: EasyPanel API client
    """

    @mcp.tool(
        name="list_services",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
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

    @mcp.tool(
        name="get_service",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
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

    @mcp.tool(
        name="update_service",
        annotations=ToolAnnotations(idempotentHint=True),
    )
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

    @mcp.tool(
        name="delete_service",
        annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True),
    )
    async def delete_service(service_id: str) -> dict[str, Any]:
        """
        Delete a service from EasyPanel. This is destructive and cannot be undone.

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

    @mcp.tool(
        name="start_service",
        annotations=ToolAnnotations(idempotentHint=True),
    )
    async def start_service(service_id: str) -> dict[str, Any]:
        """
        Start a stopped service.

        Args:
            service_id: Service ID
        """
        result = await client.start_service(service_id)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} started successfully"
        }

    @mcp.tool(
        name="stop_service",
        annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True),
    )
    async def stop_service(service_id: str) -> dict[str, Any]:
        """
        Stop a running service (takes it offline until started again).

        Args:
            service_id: Service ID
        """
        result = await client.stop_service(service_id)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} stopped successfully"
        }

    @mcp.tool(name="deploy_service")
    async def deploy_service(service_id: str) -> dict[str, Any]:
        """
        Deploy / redeploy a service (pulls the latest source/image and restarts).

        Args:
            service_id: Service ID
        """
        result = await client.deploy_service(service_id)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} deployment triggered"
        }

    @mcp.tool(
        name="scale_service",
        annotations=ToolAnnotations(idempotentHint=True),
    )
    async def scale_service(
        service_id: str,
        cpu: Optional[int] = None,
        memory: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Vertically scale a service's resources.

        Args:
            service_id: Service ID
            cpu: New CPU limit (cores)
            memory: New memory limit (MB)
        """
        result = await client.scale_service(service_id, cpu=cpu, memory=memory)
        return {
            "success": True,
            "data": result,
            "message": f"Service {service_id} scaled (cpu={cpu}, memory={memory})"
        }

    @mcp.tool(name="auto_scale_service")
    async def auto_scale_service(
        service_id: str,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        max_cpu: int = 8,
        max_memory: int = 16384,
    ) -> dict[str, Any]:
        """
        Auto-scale a service based on current system resource usage. Doubles CPU
        and/or memory (capped at max_cpu/max_memory) when usage exceeds the given
        thresholds; otherwise makes no change.

        Args:
            service_id: Service ID
            cpu_threshold: CPU usage % above which to scale up
            memory_threshold: Memory usage % above which to scale up
            max_cpu: Maximum CPU cores to scale to
            max_memory: Maximum memory (MB) to scale to
        """
        result = await client.auto_scale_service(
            service_id,
            cpu_threshold=cpu_threshold,
            memory_threshold=memory_threshold,
            max_cpu=max_cpu,
            max_memory=max_memory,
        )
        return {
            "success": True,
            "data": result,
            "message": f"Auto-scale evaluated for service {service_id}"
        }

    @mcp.tool(
        name="get_service_logs",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_service_logs(service_id: str, lines: int = 100) -> dict[str, Any]:
        """
        Get a status/diagnostics summary for a service.

        Note: EasyPanel's tRPC API does not expose raw container log streaming,
        so this returns a structured status summary (state, deployment status,
        resources, errors) derived from service inspection.

        Args:
            service_id: Service ID
            lines: Reserved for future raw-log support (currently unused)
        """
        logs = await client.get_service_logs(service_id, lines)
        return {
            "success": True,
            "data": logs,
            "message": f"Retrieved status summary for service {service_id}"
        }
