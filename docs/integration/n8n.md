---
title: n8n Integration - EasyPanel MCP
description: Integrate EasyPanel MCP with n8n using its native MCP Client nodes for infrastructure automation and AI agent tools.
keywords: n8n EasyPanel, MCP Client, Streamable HTTP, workflow automation, deployment automation, infrastructure orchestration
---

# ⚡ n8n Integration

Connect n8n directly to EasyPanel MCP using n8n's native MCP client nodes.

---

## Overview

EasyPanel MCP can expose its tools remotely through **Streamable HTTP**, the recommended HTTP transport in MCP SDK v2.

Use:

- **MCP Client** when you want to call an EasyPanel MCP tool as a regular workflow step.
- **MCP Client Tool** when you want to expose EasyPanel MCP tools to an n8n AI Agent.

This avoids manually constructing MCP JSON-RPC requests in an HTTP Request node. The MCP client handles protocol negotiation, tool discovery, schemas, and tool calls for you.

---

## 📋 Prerequisites

- An n8n instance with MCP Client support.
- EasyPanel MCP installed and configured.
- A valid `EASYPANEL_URL` and `EASYPANEL_API_KEY` on the EasyPanel MCP server.
- Network access from n8n to the EasyPanel MCP endpoint.

---

## 🔧 Start EasyPanel MCP in HTTP mode

Using the installed entrypoint:

```bash
easypanel-mcp http
```

Or directly from the repository:

```bash
python src/server.py http
```

By default, the MCP endpoint is:

```text
http://127.0.0.1:8080/mcp
```

When n8n runs on another machine or container, replace `127.0.0.1` with a hostname or address that n8n can actually reach. In production, expose the endpoint through HTTPS and an appropriate reverse proxy.

---

## 🧩 Option 1: MCP Client node

Use the **MCP Client** node when an EasyPanel action should be a normal step in a workflow.

Configure:

| Setting | Value |
| --- | --- |
| Server Transport | Streamable HTTP |
| MCP Endpoint URL | `https://your-mcp-host.example.com/mcp` |
| Authentication | According to your reverse proxy / deployment |
| Tool | Select one of the tools discovered from EasyPanel MCP |

n8n automatically fetches the available tools from the MCP server. For nested tool arguments, use the node's JSON input mode when appropriate.

Typical workflow examples:

```text
GitHub Trigger
    ↓
MCP Client: deploy_service
    ↓
Slack / Email notification
```

```text
Schedule Trigger
    ↓
MCP Client: get_system_stats
    ↓
IF / Code
    ↓
MCP Client: scale_service
```

```text
Error / Monitoring Trigger
    ↓
MCP Client: get_service
    ↓
MCP Client: restart_service
```

---

## 🤖 Option 2: MCP Client Tool for AI Agents

Use **MCP Client Tool** when an n8n AI Agent should decide which EasyPanel tool to call.

1. Add an **AI Agent** node.
2. Attach an **MCP Client Tool** to the agent's Tools input.
3. Select **Streamable HTTP** as the server transport.
4. Set the MCP endpoint to your EasyPanel MCP `/mcp` URL.
5. Limit the exposed tools when the agent only needs a subset.

For infrastructure automation, prefer exposing only the tools required by that workflow. Keep destructive actions such as service or project deletion out of general-purpose agents unless the workflow includes suitable approval controls.

---

## 🔁 Legacy SSE compatibility

Current n8n MCP Client versions support selecting the server transport. Older MCP Client Tool versions may only expose an **SSE Endpoint** field.

For those integrations, EasyPanel MCP keeps an explicit SSE mode:

```bash
easypanel-mcp sse
```

Prefer Streamable HTTP for new deployments.

---

## 🔐 Security recommendations

- Do not send `EASYPANEL_API_KEY` from n8n to the MCP endpoint. The key belongs on the EasyPanel MCP server itself.
- Put remote MCP deployments behind HTTPS.
- Use network restrictions and/or reverse-proxy authentication when the endpoint is reachable outside a trusted network.
- Expose the minimum set of MCP tools needed by an AI Agent.
- Add human approval around destructive infrastructure operations where appropriate.

---

## 🆘 Troubleshooting

### Connection refused

1. Confirm EasyPanel MCP is running with `easypanel-mcp http`.
2. Confirm n8n can reach the configured host and port.
3. Do not use `127.0.0.1` if n8n and EasyPanel MCP are in different containers or machines.
4. Check firewall and reverse-proxy rules.

### Tools do not appear

1. Verify the endpoint ends in `/mcp` for Streamable HTTP.
2. Confirm the MCP Client node is using the correct server transport.
3. Check the EasyPanel MCP logs for protocol or connection errors.
4. Confirm the server starts successfully with valid EasyPanel credentials.

### Authentication to EasyPanel fails

1. Verify `EASYPANEL_URL` on the MCP server.
2. Verify `EASYPANEL_API_KEY` or `email:password` credentials.
3. Check whether the EasyPanel credential has expired or lost permissions.

---

## 📚 Related Documentation

- **[Claude Desktop](claude-desktop.md)** - Local MCP client integration
- **[GitHub Actions](github-actions.md)** - CI/CD pipelines
- **[Tools Reference](../tools/overview.md)** - Available EasyPanel MCP tools

---

<p align="center" markdown>
**⚡ n8n + EasyPanel MCP:** native MCP transport, no hand-written protocol requests.
</p>
