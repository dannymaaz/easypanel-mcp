"""
Basic tests for EasyPanel MCP Server.

Tests cover configuration, client, and tools functionality using MCPServer.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server import MCPServer

from config import Config, EasyPanelConfig, ServerConfig
from src.client import EasyPanelClient
from src.tools import register_all_tools


class TestConfig:
    """Test configuration module."""

    def test_config_from_env(self):
        """Test creating config from environment variables."""
        with patch.dict('os.environ', {
            'EASYPANEL_URL': 'http://test.com',
            'EASYPANEL_API_KEY': 'test_key',
            'EASYPANEL_TIMEOUT': '60',
            'MCP_PORT': '9000'
        }):
            config = Config.from_env()

            assert config.easypanel.base_url == 'http://test.com'
            assert config.easypanel.api_key == 'test_key'
            assert config.easypanel.timeout == 60
            assert config.server.port == 9000

    def test_config_validate(self):
        """Test configuration validation."""
        config = Config(
            easypanel=EasyPanelConfig(api_key='test_key', base_url='http://test.com'),
            server=ServerConfig()
        )

        assert config.validate() is True

    def test_config_validate_missing_api_key(self):
        """Test validation fails without API key."""
        config = Config(
            easypanel=EasyPanelConfig(api_key='', base_url='http://test.com'),
            server=ServerConfig()
        )

        with pytest.raises(ValueError, match="EASYPANEL_API_KEY is required"):
            config.validate()


class TestEasyPanelClient:
    """Test EasyPanel API client."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        config = EasyPanelConfig(
            base_url='http://test.com',
            api_key='test_key',
            timeout=30
        )
        return EasyPanelClient(config)

    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test client connection."""
        await client.connect()

        assert client._client is not None
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test client disconnection."""
        await client.connect()
        await client.disconnect()

        assert client._client is None

    @pytest.mark.asyncio
    async def test_request_without_connection(self, client):
        """Test request fails without connection."""
        with pytest.raises(RuntimeError, match="Client not connected"):
            await client._trpc_request("projects.listProjects")


class TestMCPServerIntegration:
    """Test tools integration using MCPServer."""

    @pytest.fixture
    def mock_client(self):
        """Create mock EasyPanel client with predefined returns."""
        client = AsyncMock()
        client.list_services = AsyncMock(return_value=[
            {"id": "svc_1", "name": "test-service", "type": "app"}
        ])
        client.get_service = AsyncMock(return_value={"id": "svc_1", "type": "app"})
        client.create_service = AsyncMock(return_value={"id": "svc_new"})
        client.delete_service = AsyncMock(return_value={"deleted": True})
        client.restart_service = AsyncMock(return_value={"status": "restarting"})
        client.get_service_logs = AsyncMock(return_value=["log line 1"])
        client.list_deployments = AsyncMock(return_value=[])
        client.list_networks = AsyncMock(return_value=[])
        client.create_network = AsyncMock(return_value={"name": "test-net"})
        client.list_projects = AsyncMock(return_value=[])
        # Newly exposed tools
        client.start_service = AsyncMock(return_value={"status": "starting"})
        client.stop_service = AsyncMock(return_value={"status": "stopping"})
        client.deploy_service = AsyncMock(return_value={"status": "deploying"})
        client.scale_service = AsyncMock(return_value={"cpu": 2, "memory": 4096})
        client.auto_scale_service = AsyncMock(return_value={"scaled": False})
        client.get_system_stats = AsyncMock(return_value={"cpu": 10, "mem": 20})
        client.get_service_stats = AsyncMock(return_value={"svc_1": {"cpu": 5}})
        client.health_check = AsyncMock(return_value=True)
        client.get_server_ip = AsyncMock(return_value="203.0.113.10")
        client.list_domains = AsyncMock(return_value=[{"name": "app.example.com"}])
        client.create_domain = AsyncMock(return_value={"name": "new.example.com"})
        return client

    @pytest.fixture
    def mcp_server(self, mock_client):
        """Create MCPServer and register mock client tools."""
        mcp = MCPServer("test-mcp-server")
        register_all_tools(mcp, mock_client)
        return mcp

    @pytest.mark.asyncio
    async def test_list_services(self, mcp_server):
        """Test listing services tool via MCPServer."""
        results = await mcp_server.call_tool("list_services", {})
        # results is (content_list, return_dict)
        res_data = results[1]
        assert res_data["success"] is True
        assert len(res_data["data"]) == 1
        assert res_data["data"][0]["name"] == "test-service"

    @pytest.mark.asyncio
    async def test_get_service(self, mcp_server):
        """Test getting service details tool via MCPServer."""
        results = await mcp_server.call_tool("get_service", {"service_id": "svc_1"})
        res_data = results[1]
        assert res_data["success"] is True
        assert res_data["data"]["id"] == "svc_1"

    @pytest.mark.asyncio
    async def test_create_service(self, mcp_server):
        """Test creating service tool via MCPServer."""
        results = await mcp_server.call_tool("create_service", {
            "name": "new-service",
            "project_id": "proj_1",
            "image": "nginx:latest"
        })
        res_data = results[1]
        assert res_data["success"] is True

    @pytest.mark.asyncio
    async def test_list_deployments(self, mcp_server):
        """Test listing deployments tool via MCPServer."""
        results = await mcp_server.call_tool("list_deployments", {})
        res_data = results[1]
        assert res_data["success"] is True

    @pytest.mark.asyncio
    async def test_create_network(self, mcp_server):
        """Test creating network tool via MCPServer."""
        results = await mcp_server.call_tool("create_network", {
            "name": "internal-net",
            "internal": True
        })
        res_data = results[1]
        assert res_data["success"] is True
        assert "internal" in res_data["message"]

    @pytest.mark.asyncio
    async def test_list_projects(self, mcp_server):
        """Test listing projects tool via MCPServer."""
        results = await mcp_server.call_tool("list_projects", {})
        res_data = results[1]
        assert res_data["success"] is True

    # ----- Newly exposed tools -----

    @pytest.mark.asyncio
    async def test_all_expected_tools_registered(self, mcp_server):
        """The previously-unexposed client methods must now be real tools."""
        names = {t.name for t in await mcp_server.list_tools()}
        for expected in [
            "start_service", "stop_service", "deploy_service", "scale_service",
            "auto_scale_service", "get_system_stats", "get_service_stats",
            "health_check", "get_server_ip", "list_domains", "create_domain",
        ]:
            assert expected in names, f"Tool {expected} should be registered"

    @pytest.mark.asyncio
    async def test_stop_service(self, mcp_server, mock_client):
        """stop_service tool should call the client and succeed."""
        results = await mcp_server.call_tool("stop_service", {"service_id": "svc_1"})
        assert results[1]["success"] is True
        mock_client.stop_service.assert_awaited_once_with("svc_1")

    @pytest.mark.asyncio
    async def test_start_service(self, mcp_server, mock_client):
        """start_service tool should call the client and succeed."""
        results = await mcp_server.call_tool("start_service", {"service_id": "svc_1"})
        assert results[1]["success"] is True
        mock_client.start_service.assert_awaited_once_with("svc_1")

    @pytest.mark.asyncio
    async def test_scale_service(self, mcp_server, mock_client):
        """scale_service tool should forward cpu/memory to the client."""
        results = await mcp_server.call_tool(
            "scale_service", {"service_id": "svc_1", "cpu": 2, "memory": 4096}
        )
        assert results[1]["success"] is True
        mock_client.scale_service.assert_awaited_once_with("svc_1", cpu=2, memory=4096)

    @pytest.mark.asyncio
    async def test_get_system_stats(self, mcp_server):
        """get_system_stats tool should return the system stats."""
        results = await mcp_server.call_tool("get_system_stats", {})
        assert results[1]["success"] is True
        assert results[1]["data"]["cpu"] == 10

    @pytest.mark.asyncio
    async def test_health_check(self, mcp_server):
        """health_check tool should report a healthy API."""
        results = await mcp_server.call_tool("health_check", {})
        assert results[1]["data"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_list_domains(self, mcp_server):
        """list_domains tool should return domains."""
        results = await mcp_server.call_tool("list_domains", {})
        assert results[1]["success"] is True
        assert results[1]["data"][0]["name"] == "app.example.com"


class TestRequestRouting:
    """Test the GET (query) vs POST (mutation) routing and namespace caching."""

    @pytest.fixture
    def client(self):
        return EasyPanelClient(EasyPanelConfig(
            base_url="http://test.com", api_key="test_key", timeout=30
        ))

    @pytest.mark.asyncio
    async def test_query_uses_get_mutation_uses_post(self, client):
        """list/get/inspect -> GET; create/destroy/deploy/stop -> POST."""
        await client.connect()
        try:
            calls = {"GET": [], "POST": []}

            async def fake_get(endpoint, params=None):
                calls["GET"].append(endpoint)
                resp = MagicMock()
                resp.raise_for_status = MagicMock()
                resp.json = MagicMock(return_value={"result": {"data": {"json": {}}}})
                return resp

            async def fake_post(endpoint, json=None):
                calls["POST"].append(endpoint)
                resp = MagicMock()
                resp.raise_for_status = MagicMock()
                resp.json = MagicMock(return_value={"result": {"data": {"json": {}}}})
                return resp

            client._client.get = fake_get
            client._client.post = fake_post

            await client._trpc_request("projects.listProjects")
            await client._trpc_request("services.app.inspectService", {"id": "x"})
            await client._trpc_request("monitor.getSystemStats")
            await client._trpc_request("services.app.createService", {"name": "x"})
            await client._trpc_request("services.app.destroyService", {"id": "x"})
            await client._trpc_request("services.app.stopService", {"id": "x"})

            assert calls["GET"] == [
                "/api/trpc/projects.listProjects",
                "/api/trpc/services.app.inspectService",
                "/api/trpc/monitor.getSystemStats",
            ]
            assert calls["POST"] == [
                "/api/trpc/services.app.createService",
                "/api/trpc/services.app.destroyService",
                "/api/trpc/services.app.stopService",
            ]
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_namespace_cache_fetches_tree_once(self, client):
        """Resolving namespaces for several services should hit the tree once."""
        tree = [{
            "id": "proj_1",
            "services": [
                {"id": "svc_app", "type": "app"},
                {"id": "svc_pg", "type": "postgres"},
                {"id": "svc_redis", "type": "redis"},
            ],
        }]
        with patch.object(client, "_trpc_request", new=AsyncMock(return_value=tree)) as req:
            ns_app = await client._resolve_service_namespace("svc_app")
            ns_pg = await client._resolve_service_namespace("svc_pg")
            ns_redis = await client._resolve_service_namespace("svc_redis")

        assert ns_app == "services.app"
        assert ns_pg == "services.postgres"
        assert ns_redis == "services.redis"
        # Three resolutions, but only ONE listProjectsAndServices round-trip.
        req.assert_awaited_once()


class TestEmailPasswordAuth:
    """Test tRPC email:password authentication."""

    @pytest.fixture
    def client(self):
        """Create test client using email:password credentials."""
        config = EasyPanelConfig(
            base_url='http://test.com',
            api_key='user@example.com:secret',
            timeout=30
        )
        return EasyPanelClient(config)

    def _stub_login(self, client, payload):
        """Point the client at a stubbed auth.login response."""
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json = MagicMock(return_value=payload)
        client._client = AsyncMock()
        client._client.post = AsyncMock(return_value=response)
        client._client.headers = {}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", [
        {"result": {"data": {"json": {"token": "tok_123"}}}},
        {"json": {"token": "tok_123"}},
        {"token": "tok_123"},
    ])
    async def test_reads_token_from_known_response_shapes(self, client, payload):
        """auth.login returns different shapes across EasyPanel versions."""
        self._stub_login(client, payload)

        await client._authenticate_with_email_password()

        assert client._token == "tok_123"
        assert client._client.headers["Authorization"] == "tok_123"

    @pytest.mark.asyncio
    async def test_missing_token_raises(self, client):
        """A login response with no token is still an error."""
        self._stub_login(client, {"result": {"data": {"json": {}}}})

        with pytest.raises(RuntimeError, match="No token received"):
            await client._authenticate_with_email_password()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
