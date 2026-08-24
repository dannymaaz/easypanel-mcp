---
title: Changelog - EasyPanel MCP
description: Changelog and release history for EasyPanel MCP.
keywords: EasyPanel changelog, release notes, version history, updates
---

# 📋 Changelog

All notable changes to EasyPanel MCP.

---

## [2.0.0] - 2026-08-24

### 🚀 MCP SDK v2 migration

This release migrates EasyPanel MCP to the stable 2.x line of the official MCP Python SDK.

### Breaking changes

- Replaced `FastMCP` with `MCPServer` from MCP Python SDK v2.
- The `http` launch mode now uses **Streamable HTTP** at `/mcp` instead of being mapped internally to SSE.
- MCP SDK support is now `mcp>=2.0.0,<3.0.0`.

### Compatibility

- `stdio` remains the default transport for local MCP clients.
- `sse` remains available as an explicit legacy transport.
- Streamable HTTP is the recommended remote transport for new integrations.
- Tested with MCP Python SDK 2.1.0 on Python 3.10, 3.11 and 3.12.

### Improvements

- Added a portable installed CLI entrypoint: `easypanel-mcp`.
- Direct execution of `src/server.py` now resolves project imports even when launched outside the repository working directory.
- Improved EasyPanel `auth.login` compatibility by accepting wrapped, bare JSON and top-level token response shapes.
- Updated tool integration tests for MCP v2 `CallToolResult` and structured tool output.
- Added regression coverage for `stdio`, `http`/Streamable HTTP and `sse` transport selection.
- Updated the n8n guide to use native MCP Client and MCP Client Tool nodes instead of manually constructed MCP requests.
- Updated GitHub Actions to current major versions and consolidated CI dependency maintenance.
- Improved README discovery links and security guidance.

### Quality and release process

- CI validates the test suite on Python 3.10, 3.11 and 3.12.
- Release validation now also includes Ruff, mypy, strict MkDocs builds and Python package builds.

---

## [1.0.0] - 2026-03-14

### 🎉 Initial Release

#### ✨ Features

- **Core MCP Server**
  - Full MCP protocol implementation
  - stdio and HTTP transport modes
  - Async architecture for high performance

- **Services Tools** (7 tools)
  - `list_services` - List all services
  - `get_service` - Get service details
  - `create_service` - Create new services
  - `update_service` - Update configuration
  - `delete_service` - Remove services
  - `restart_service` - Restart running services
  - `get_service_logs` - View service logs

- **Deployments Tools** (4 tools)
  - `list_deployments` - List all deployments
  - `get_deployment` - Get deployment details
  - `create_deployment` - Create new deployment
  - `get_deployment_logs` - View deployment logs

- **Networks Tools** (3 tools)
  - `list_networks` - List all networks
  - `create_network` - Create networks (public or internal)
  - `delete_network` - Delete networks

- **Projects Tools** (4 tools)
  - `list_projects` - List all projects
  - `get_project` - Get project details
  - `create_project` - Create new project
  - `delete_project` - Delete project

#### 🔧 Configuration

- Environment-based configuration
- Support for custom timeouts
- SSL verification options
- Debug mode for troubleshooting

#### 📚 Documentation

- Complete MkDocs documentation
- Minimalist blue-themed design
- SEO optimized
- Integration guides for Claude Desktop, n8n and GitHub Actions

#### 🧪 Testing

- Unit and integration test coverage with pytest
- Cross-platform support for Windows, macOS and Linux
- Python 3.10+

---

## 📊 Version Compatibility

| EasyPanel MCP | Python | EasyPanel | MCP Python SDK |
|---------------|--------|-----------|----------------|
| 2.0.0         | 3.10+  | Any       | >=2.0.0,<3.0.0 |
| 1.0.0         | 3.10+  | Any       | 1.x |

---

## 🐛 Known Issues

No release-blocking issues are currently documented.

---

## 🤝 Contributing

Contributions are welcome. Please fork the repository, create a focused branch, add or update tests where appropriate, and submit a pull request.

---

## 📜 License

MIT License - See [LICENSE](https://github.com/dannymaaz/easypanel-mcp/blob/main/LICENSE)

---

<p align="center" markdown>
**Built with ❤️ by Danny Maaz**
</p>
