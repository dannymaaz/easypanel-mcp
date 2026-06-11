"""
Configuration module for EasyPanel MCP Server.

Handles environment variables and configuration settings.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class EasyPanelConfig:
    """Configuration for EasyPanel API connection."""
    
    base_url: str = os.getenv("EASYPANEL_URL", "http://localhost:3000")
    api_key: str = os.getenv("EASYPANEL_API_KEY", "")
    timeout: int = int(os.getenv("EASYPANEL_TIMEOUT", "30"))
    verify_ssl: bool = os.getenv("EASYPANEL_VERIFY_SSL", "true").lower() == "true"


@dataclass
class ServerConfig:
    """Configuration for MCP Server."""
    
    host: str = os.getenv("MCP_HOST", "127.0.0.1")
    port: int = int(os.getenv("MCP_PORT", "8080"))
    log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")
    debug: bool = os.getenv("MCP_DEBUG", "false").lower() == "true"


@dataclass
class Config:
    """Main configuration class."""
    
    easypanel: EasyPanelConfig
    server: ServerConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            easypanel=EasyPanelConfig(
                base_url=os.getenv("EASYPANEL_URL", "http://localhost:3000"),
                api_key=os.getenv("EASYPANEL_API_KEY", ""),
                timeout=int(os.getenv("EASYPANEL_TIMEOUT", "30")),
                verify_ssl=os.getenv("EASYPANEL_VERIFY_SSL", "true").lower() == "true"
            ),
            server=ServerConfig(
                host=os.getenv("MCP_HOST", "127.0.0.1"),
                port=int(os.getenv("MCP_PORT", "8080")),
                log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
                debug=os.getenv("MCP_DEBUG", "false").lower() == "true"
            )
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.easypanel.api_key:
            raise ValueError("EASYPANEL_API_KEY is required")
        if not self.easypanel.base_url:
            raise ValueError("EASYPANEL_URL is required")
        return True


# Global configuration instance
config = Config.from_env()
