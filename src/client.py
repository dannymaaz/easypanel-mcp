"""
Enhanced EasyPanel Client with advanced features.

Adds support for logs, networks discovery, and auto-scaling
by combining tRPC API calls with smart inference.
"""

import httpx
import logging
import json
from typing import Any, Optional
from config import EasyPanelConfig

logger = logging.getLogger(__name__)


class EasyPanelClient:
    """Enhanced client for interacting with EasyPanel API using tRPC."""

    def __init__(self, config: EasyPanelConfig):
        """
        Initialize EasyPanel client.

        Args:
            config: EasyPanel configuration settings
        """
        self.base_url = config.base_url.rstrip("/")
        self.api_key = config.api_key
        self.timeout = config.timeout
        self.verify_ssl = config.verify_ssl

        self._client: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None

    async def connect(self) -> None:
        """Establish connection to EasyPanel API."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        
        # If API key looks like email:password, authenticate via tRPC
        if ":" in self.api_key and "@" in self.api_key:
            await self._authenticate_with_email_password()
        else:
            # Use API key as Bearer token (session token)
            self._client.headers["Authorization"] = f"Bearer {self.api_key}"
            logger.info(f"Connected to EasyPanel at {self.base_url} (Bearer token auth)")

    async def _authenticate_with_email_password(self) -> None:
        """Authenticate using email and password via tRPC."""
        try:
            email, password = self.api_key.split(":", 1)
            response = await self._client.post(
                "/api/trpc/auth.login",
                json={"json": {"email": email, "password": password}}
            )
            response.raise_for_status()
            result = response.json()
            token = result.get("result", {}).get("data", {}).get("json", {}).get("token")
            
            if token:
                self._token = token
                self._client.headers["Authorization"] = token
                logger.info(f"Authenticated to EasyPanel as {email}")
            else:
                raise RuntimeError("No token received from auth.login")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to EasyPanel API."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from EasyPanel")

    async def _trpc_request(
        self,
        procedure: str,
        input_data: Optional[dict[str, Any]] = None,
        method: str = "POST"
    ) -> Any:
        """
        Make tRPC request to EasyPanel API.

        Args:
            procedure: tRPC procedure name (e.g., "projects.listProjects")
            input_data: Input data for the procedure
            method: HTTP method (GET or POST). GET is used for query procedures.

        Returns:
            tRPC response data (the json payload inside result.data.json)

        Raises:
            RuntimeError: If request fails
        """
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")

        endpoint = f"/api/trpc/{procedure}"
        
        try:
            # Query procedures (list, get, inspect, stats, info) use GET
            # Mutation procedures (create, update, delete) use POST
            query_procedures = ["list", "get", "inspect", "stats", "info", "check", "public"]
            is_query = any(q in procedure.lower() for q in query_procedures)
            
            if is_query or method == "GET":
                # tRPC GET requests encode input as JSON string in query param
                if input_data:
                    input_json = json.dumps(input_data)
                    response = await self._client.get(endpoint, params={"input": input_json})
                else:
                    response = await self._client.get(endpoint)
            else:
                # tRPC POST requests send JSON body with "json" wrapper
                payload = {"json": input_data} if input_data else {}
                response = await self._client.post(endpoint, json=payload)
            
            response.raise_for_status()
            result = response.json()
            
            # Extract data from tRPC response structure:
            # { "result": { "data": { "json": {...}, "meta": {...} } } }
            data = result.get("result", {}).get("data", {})
            if "json" in data:
                return data["json"]
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("json", {}).get("message", error_msg)
            except:
                pass
            logger.error(f"tRPC error [{procedure}]: {error_msg}")
            raise RuntimeError(f"tRPC error: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"Request error [{procedure}]: {str(e)}")
            raise

    # ========== Helper: Dynamic Namespace Resolution ==========
    
    async def _resolve_service_namespace(self, service_id: str) -> str:
        """
        Resolve the correct tRPC namespace for a service dynamically based on its type.
        E.g., 'services.app', 'services.postgres', 'services.redis', etc.
        """
        try:
            result = await self._trpc_request("projects.listProjectsAndServices")
            projects = result.get("data", []) if isinstance(result, dict) else result
            
            for proj in (projects if isinstance(projects, list) else []):
                for service in proj.get("services", []):
                    if service.get("id") == service_id:
                        service_type = service.get("type", "app")
                        
                        # Valid EasyPanel service types with specific namespaces
                        valid_types = ["app", "postgres", "redis", "mysql", "mongodb", "mariadb"]
                        if service_type in valid_types:
                            return f"services.{service_type}"
                        
                        # Fallback for templates and integrations (they are managed as standard apps)
                        return "services.app"
        except Exception as e:
            logger.warning(f"Failed to dynamically resolve namespace for service {service_id}: {e}")
        
        return "services.app"

    # ========== Project Management ==========
    
    async def list_projects(self) -> list[dict[str, Any]]:
        """List all projects."""
        try:
            result = await self._trpc_request("projects.listProjects")
            if isinstance(result, dict) and "data" in result:
                return result.get("data", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            raise

    async def get_project(self, project_id: str) -> dict[str, Any]:
        """Get project details (inspect)."""
        try:
            result = await self._trpc_request("projects.inspectProject", {"id": project_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            raise

    async def create_project(
        self,
        name: str,
        description: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new project."""
        try:
            data = {"name": name}
            if description:
                data["description"] = description
            result = await self._trpc_request("projects.createProject", data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    async def delete_project(self, project_id: str) -> dict[str, Any]:
        """Delete a project."""
        try:
            result = await self._trpc_request("projects.destroyProject", {"id": project_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            raise

    # ========== Service Management ==========
    
    async def list_services(self, project_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List all services, optionally filtered by project."""
        try:
            result = await self._trpc_request("projects.listProjectsAndServices")
            projects = result.get("data", []) if isinstance(result, dict) else result
            
            if project_id:
                for proj in projects:
                    if proj.get("id") == project_id:
                        return proj.get("services", [])
                return []
            else:
                services = []
                for proj in projects:
                    services.extend(proj.get("services", []))
                return services
        except Exception as e:
            logger.error(f"Error listing services: {e}")
            raise

    async def get_service(self, service_id: str) -> dict[str, Any]:
        """Get service details (inspect)."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.inspectService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error getting service: {e}")
            raise

    async def create_service(
        self,
        name: str,
        project_id: str,
        image: str,
        config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Create a new service (app type)."""
        try:
            data = {
                "projectId": project_id,
                "name": name,
                "sourceImage": image,
                **(config or {})
            }
            result = await self._trpc_request("services.app.createService", data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            raise

    async def update_service(
        self,
        service_id: str,
        config: dict[str, Any]
    ) -> dict[str, Any]:
        """Update service configuration."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            data = {"id": service_id, **config}
            
            # Try different update methods based on config keys
            if "env" in config or "environment" in config:
                method = f"{namespace}.updateEnv"
            elif "resources" in config or "cpu" in config or "memory" in config:
                method = f"{namespace}.updateResources"
            elif "sourceImage" in config:
                method = f"{namespace}.updateSourceImage"
            elif "basicAuth" in config:
                method = f"{namespace}.updateBasicAuth"
            elif "ports" in config:
                method = f"{namespace}.updatePorts"
            else:
                method = f"{namespace}.updateDeploy"
            
            result = await self._trpc_request(method, data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error updating service: {e}")
            raise

    async def delete_service(self, service_id: str) -> dict[str, Any]:
        """Delete a service."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.destroyService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error deleting service: {e}")
            raise

    async def restart_service(self, service_id: str) -> dict[str, Any]:
        """Restart a service."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.restartService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error restarting service: {e}")
            raise

    async def start_service(self, service_id: str) -> dict[str, Any]:
        """Start a service."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.startService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            raise

    async def stop_service(self, service_id: str) -> dict[str, Any]:
        """Stop a service."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.stopService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
            raise

    async def deploy_service(self, service_id: str) -> dict[str, Any]:
        """Deploy/redeploy a service."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            result = await self._trpc_request(f"{namespace}.deployService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error deploying service: {e}")
            raise

    # ========== Enhanced: Service Logs (via inspection) ==========
    
    async def get_service_logs(
        self,
        service_id: str,
        lines: int = 100
    ) -> list[str]:
        """
        Get service logs by inspecting service state.
        """
        try:
            service = await self.get_service(service_id)
            
            if not service:
                return [f"Service {service_id} not found"]
            
            logs = []
            status = service.get("status", "unknown")
            state = service.get("state", "unknown")
            created_at = service.get("createdAt", "unknown")
            updated_at = service.get("updatedAt", "unknown")
            
            logs.append(f"📊 Service: {service.get('name', service_id)}")
            logs.append(f"📦 Status: {status}")
            logs.append(f"🔄 State: {state}")
            logs.append(f"📅 Created: {created_at}")
            logs.append(f"🕐 Updated: {updated_at}")
            
            error = service.get("error")
            if error:
                logs.append(f"❌ Error: {error}")
            
            deployment = service.get("deployment", {})
            if deployment:
                deploy_status = deployment.get("status", "unknown")
                logs.append(f"🚀 Deployment: {deploy_status}")
                
                deploy_error = deployment.get("error")
                if deploy_error:
                    logs.append(f"❌ Deploy Error: {deploy_error}")
            
            resources = service.get("resources", {})
            if resources:
                cpu = resources.get("cpu", "N/A")
                memory = resources.get("memory", "N/A")
                logs.append(f"💻 CPU: {cpu}")
                logs.append(f"🧠 Memory: {memory}")
            
            if status == "error" or state == "error":
                logs.append("")
                logs.append("⚠️ Service is in error state!")
                logs.append("💡 Try: restart_service, check resources, or inspect configuration")
            
            return logs
        except Exception as e:
            logger.error(f"Error getting service logs: {e}")
            raise

    # ========== Enhanced: Network Discovery ==========
    
    async def list_networks(self) -> list[dict[str, Any]]:
        """
        Discover networks by analyzing services and their configurations.
        """
        try:
            services = await self.list_services()
            networks = {}
            
            for service in services:
                service_name = service.get("name", "unknown")
                service_id = service.get("id", "unknown")
                project_id = service.get("projectId", "unknown")
                
                ports = service.get("ports", [])
                has_public = any(p.get("public") for p in ports) if ports else False
                
                if project_id not in networks:
                    networks[project_id] = {
                        "id": f"net-{project_id}",
                        "name": f"project-{project_id}",
                        "type": "project",
                        "services": [],
                        "internal_services": 0,
                        "public_services": 0
                    }
                
                networks[project_id]["services"].append({
                    "id": service_id,
                    "name": service_name,
                    "internal": not has_public
                })
                
                if has_public:
                    networks[project_id]["public_services"] += 1
                else:
                    networks[project_id]["internal_services"] += 1
            
            network_list = list(networks.values())
            logger.info(f"Discovered {len(network_list)} networks")
            return network_list
        except Exception as e:
            logger.error(f"Error listing networks: {e}")
            raise

    async def create_network(
        self,
        name: str,
        internal: bool = False,
        driver: str = "overlay"
    ) -> dict[str, Any]:
        """
        Create an isolated service network helper.
        """
        logger.warning(
            "EasyPanel manages networks automatically. "
            "To create isolated services, set internal=True when creating services."
        )
        return {
            "name": name,
            "internal": internal,
            "note": "Networks are auto-created by EasyPanel when services are deployed"
        }

    async def delete_network(self, network_id: str) -> dict[str, Any]:
        """
        Helper network deletion info.
        """
        logger.warning(
            "EasyPanel manages networks automatically. "
            "Delete all services in the network to remove it."
        )
        return {
            "note": "Delete all services in the network to remove it"
        }

    # ========== Deployment Management ==========
    
    async def list_deployments(self, project_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List all deployments (via services)."""
        return await self.list_services(project_id)

    async def get_deployment(self, deployment_id: str) -> dict[str, Any]:
        """Get deployment details (via service inspect)."""
        return await self.get_service(deployment_id)

    async def create_deployment(
        self,
        project_id: str,
        service_id: str,
        image: str,
        config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Create a new deployment (update service source and deploy)."""
        try:
            namespace = await self._resolve_service_namespace(service_id)
            await self._trpc_request(f"{namespace}.updateSourceImage", {
                "id": service_id,
                "sourceImage": image
            })
            result = await self._trpc_request(f"{namespace}.deployService", {"id": service_id})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error creating deployment: {e}")
            raise

    async def get_deployment_logs(self, deployment_id: str) -> list[str]:
        """Get deployment logs (via service logs)."""
        return await self.get_service_logs(deployment_id)

    # ========== System Information ==========
    
    async def get_system_info(self) -> dict[str, Any]:
        """Get system information."""
        try:
            result = await self._trpc_request("monitor.getSystemStats")
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            raise

    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics (CPU, memory, disk)."""
        try:
            result = await self._trpc_request("monitor.getSystemStats")
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            raise

    async def get_service_stats(self) -> dict[str, Any]:
        """Get service statistics."""
        try:
            result = await self._trpc_request("monitor.getServiceStats")
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            raise

    async def health_check(self) -> bool:
        """Check EasyPanel API health."""
        try:
            if not self._client:
                return False
            response = await self._client.get("/api/trpc/auth.getSession")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def get_server_ip(self) -> str:
        """Get server IP address."""
        try:
            stats = await self.get_system_stats()
            return stats.get("ip", "") if isinstance(stats, dict) else ""
        except Exception as e:
            logger.error(f"Error getting server IP: {e}")
            raise

    # ========== Enhanced: Auto-Scaling Helpers ==========
    
    async def scale_service(
        self,
        service_id: str,
        cpu: Optional[int] = None,
        memory: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Scale service resources (vertical scaling).
        """
        try:
            namespace = await self._resolve_service_namespace(service_id)
            config = {}
            if cpu:
                config["cpu"] = cpu
            if memory:
                config["memory"] = memory
            
            if not config:
                return {"error": "No scaling parameters provided"}
            
            result = await self._trpc_request(f"{namespace}.updateResources", {
                "id": service_id,
                **config
            })
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error scaling service: {e}")
            raise

    async def auto_scale_service(
        self,
        service_id: str,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        max_cpu: int = 8,
        max_memory: int = 16384
    ) -> dict[str, Any]:
        """
        Automatically scale service based on current resource usage.
        """
        try:
            service = await self.get_service(service_id)
            if not service:
                return {"error": f"Service {service_id} not found"}
            
            resources = service.get("resources", {})
            current_cpu = resources.get("cpu", 1)
            current_memory = resources.get("memory", 2048)
            
            stats = await self.get_system_stats()
            cpu_info = stats.get("cpuInfo", {})
            mem_info = stats.get("memInfo", {})
            
            cpu_usage = cpu_info.get("usedPercentage", 0)
            mem_usage = mem_info.get("usedMemPercentage", 0)
            
            scale_cpu = cpu_usage > cpu_threshold
            scale_memory = mem_usage > memory_threshold
            
            if not scale_cpu and not scale_memory:
                return {
                    "scaled": False,
                    "reason": "Resource usage below threshold",
                    "cpu_usage": cpu_usage,
                    "memory_usage": mem_usage
                }
            
            new_cpu = min(current_cpu * 2, max_cpu) if scale_cpu else current_cpu
            new_memory = min(current_memory * 2, max_memory) if scale_memory else current_memory
            
            result = await self.scale_service(service_id, cpu=new_cpu, memory=new_memory)
            return {
                "scaled": True,
                "old_cpu": current_cpu,
                "new_cpu": new_cpu,
                "old_memory": current_memory,
                "new_memory": new_memory,
                "reason": "High resource usage detected",
                "cpu_usage": cpu_usage,
                "memory_usage": mem_usage,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error auto-scaling service: {e}")
            raise

    # ========== Additional Utilities ==========
    
    async def list_domains(self, service_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List domains."""
        try:
            result = await self._trpc_request("domains.listDomains")
            if isinstance(result, dict) and "data" in result:
                return result.get("data", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Error listing domains: {e}")
            raise

    async def create_domain(
        self,
        name: str,
        service_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new domain."""
        try:
            data = {"name": name}
            if service_id:
                data["serviceId"] = service_id
            result = await self._trpc_request("domains.createDomain", data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            raise

    async def get_public_key(self) -> str:
        """Get Git public key."""
        try:
            result = await self._trpc_request("git.getPublicKey")
            if isinstance(result, dict):
                return result.get("publicKey", "")
            return str(result) if result else ""
        except Exception as e:
            logger.error(f"Error getting public key: {e}")
            raise
