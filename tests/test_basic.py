"""
Basic tests for EasyPanel MCP Server.

Tests cover configuration, client, and tools functionality using FastMCP.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp.server.fastmcp import FastMCP
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


class TestFastMCPIntegration:
    """Test tools integration using FastMCP."""

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
        return client

    @pytest.fixture
    def mcp_server(self, mock_client):
        """Create FastMCP server and register mock client tools."""
        mcp = FastMCP("test-mcp-server")
        register_all_tools(mcp, mock_client)
        return mcp

    @pytest.mark.asyncio
    async def test_list_services(self, mcp_server):
        """Test listing services tool via FastMCP."""
        results = await mcp_server.call_tool("list_services", {})
        # results is (content_list, return_dict)
        res_data = results[1]
        assert res_data["success"] is True
        assert len(res_data["data"]) == 1
        assert res_data["data"][0]["name"] == "test-service"

    @pytest.mark.asyncio
    async def test_get_service(self, mcp_server):
        """Test getting service details tool via FastMCP."""
        results = await mcp_server.call_tool("get_service", {"service_id": "svc_1"})
        res_data = results[1]
        assert res_data["success"] is True
        assert res_data["data"]["id"] == "svc_1"

    @pytest.mark.asyncio
    async def test_create_service(self, mcp_server):
        """Test creating service tool via FastMCP."""
        results = await mcp_server.call_tool("create_service", {
            "name": "new-service",
            "project_id": "proj_1",
            "image": "nginx:latest"
        })
        res_data = results[1]
        assert res_data["success"] is True

    @pytest.mark.asyncio
    async def test_list_deployments(self, mcp_server):
        """Test listing deployments tool via FastMCP."""
        results = await mcp_server.call_tool("list_deployments", {})
        res_data = results[1]
        assert res_data["success"] is True

    @pytest.mark.asyncio
    async def test_create_network(self, mcp_server):
        """Test creating network tool via FastMCP."""
        results = await mcp_server.call_tool("create_network", {
            "name": "internal-net",
            "internal": True
        })
        res_data = results[1]
        assert res_data["success"] is True
        assert "internal" in res_data["message"]

    @pytest.mark.asyncio
    async def test_list_projects(self, mcp_server):
        """Test listing projects tool via FastMCP."""
        results = await mcp_server.call_tool("list_projects", {})
        res_data = results[1]
        assert res_data["success"] is True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
