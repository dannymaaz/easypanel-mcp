---
title: Advanced Features Guide - EasyPanel MCP
description: Complete guide to security, isolated networks, deployment, debugging, auto-scaling and advanced features in EasyPanel MCP.
keywords: EasyPanel security, isolated networks, auto-scaling, debugging, deployment, Docker, advanced features
---

# Guía de Características Avanzadas

Esta guía detalla las funciones avanzadas de **seguridad**, **redes aisladas**, **despliegue**, **depuración**, **escalado automático** y la integración de EasyPanel MCP con IDEs modernos.

---

## Características de Seguridad

### Herramientas de Seguridad Disponibles

EasyPanel MCP ofrece las siguientes capacidades relacionadas con la seguridad:

| Característica | Estado | Descripción |
|---|---|---|
| **Autenticación por API Key** | :material-check-circle: Disponible | Autenticación segura mediante Bearer token |
| **Autenticación por Email/Password** | :material-check-circle: Disponible | Método de autenticación alternativo |
| **Gestión de Sesiones** | :material-check-circle: Disponible | Manejo automático del token de sesión |
| **Verificación SSL/TLS** | :material-check-circle: Disponible | Verificación SSL configurable |
| **Redes Internas** | :material-alert: Vía Config de Servicio | Redes aisladas a través de la configuración del servicio |
| **Autenticación Básica (Basic Auth)** | :material-check-circle: Disponible | Autenticación básica HTTP para servicios |
| **Gestión de Dominios** | :material-check-circle: Disponible | Configuración de dominios personalizados |
| **Control de Exposición de Puertos** | :material-check-circle: Disponible | Gestión de puertos expuestos |


### Security Best Practices

#### 1. Use API Keys (Recommended)

```bash
# Generate API key in EasyPanel Dashboard
# Settings → API Keys → Create New Key

# Use in .env
EASYPANEL_API_KEY=ep_live_xxxxxxxxxxxxx
```

**Advantages:**
- More secure than password
- Can be rotated easily
- Can be revoked without changing password
- No plaintext password storage

#### 2. Isolated Networks (Internal Services)

EasyPanel manages networks automatically. To create isolated services:

```json
// Ask your AI agent:
"Create a PostgreSQL service in an isolated network"

// The AI will configure:
{
  "name": "postgres-db",
  "projectId": "your-project",
  "sourceImage": "postgres:15",
  "internal": true  // ← Isolated from internet
}
```

**What happens:**
- EasyPanel creates an internal Docker network
- Service is only accessible by other services in the same network
- No public exposure

#### 3. Environment Variables Security

```bash
# Ask AI to set sensitive env vars:
"Set DATABASE_URL environment variable for my-api service"

// The AI will use:
services.app.updateEnv with encrypted values
```

#### 4. Port Management

Control which ports are exposed:

```json
// Ask your AI:
"Expose port 8080 for my-api service but keep database internal"

// Configuration:
{
  "ports": [
    {"public": 80, "private": 8080, "protocol": "http"}
  ]
}
```

---

## Redes Aisladas

### How EasyPanel Handles Networks

EasyPanel **automatically manages Docker networks**. You don't need to create networks manually.

**Network Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| **Public Network** | Services accessible from internet | Web apps, APIs |
| **Internal Network** | Services only accessible internally | Databases, caches |
| **Project Network** | Services within same project can communicate | Microservices |

### Creating Isolated Services

#### Method 1: Ask Your AI Agent

```
User: "Create a Redis database that's only accessible internally"

AI: 📦 Creating Redis service...
    🔗 Configuring internal network...
    ✅ Service 'redis-cache' created (internal only)
    🔒 Not exposed to internet
```

#### Method 2: Manual Configuration

```json
{
  "name": "redis-internal",
  "projectId": "proj_xxx",
  "sourceImage": "redis:7",
  "env": {
    "REDIS_PASSWORD": "secure_password"
  },
  "ports": [],  // ← No public ports = internal only
  "internal": true
}
```

### Service-to-Service Communication

Services in the same project can communicate automatically:

```
┌─────────────┐         ┌──────────────┐
│  API App    │ ──────► │  PostgreSQL  │
│  (Public)   │  Internal│  (Private)   │
└─────────────┘  Network└──────────────┘
```

**Example:**
```bash
# API can connect to database via:
DATABASE_URL=postgres://user:pass@postgres-db:5432/mydb

# But database is NOT accessible from internet
```

---

## Características de Despliegue

### Available Deployment Tools

| Tool | Description | Example |
|------|-------------|---------|
| `create_service` | Create and deploy a service | Deploy Docker image |
| `deploy_service` | Redeploy existing service | Apply new configuration |
| `update_source_image` | Update Docker image | Deploy new version |
| `update_source_github` | Connect GitHub repo | Auto-deploy from Git |
| `update_source_git` | Connect Git repository | Deploy from Git URL |
| `update_env` | Update environment variables | Change config |
| `update_resources` | Update CPU/Memory | Scale resources |
| `restart_service` | Restart service | Apply changes |
| `start_service` / `stop_service` | Control service state | Maintenance mode |

### Deployment Methods

#### 1. Docker Image Deployment

```
User: "Deploy nginx latest version in my project"

AI: 🚀 Deploying nginx:latest...
    ✅ Service created
    🌐 Available at: https://nginx.your-domain.com
```

#### 2. GitHub Deployment

```
User: "Deploy my GitHub repository myuser/myapp"

AI: 🔗 Connecting to GitHub...
    📦 Cloning repository...
    🏗️ Building from Dockerfile...
    ✅ Deployed successfully!
```

#### 3. Git URL Deployment

```
User: "Deploy from https://gitlab.com/user/repo.git"

AI: 📥 Fetching from GitLab...
    🔨 Building...
    ✅ Deployment complete!
```

### Deployment Workflow

```
1. Create Service
   ↓
2. Configure Source (Image/Git/GitHub)
   ↓
3. Set Environment Variables
   ↓
4. Configure Ports
   ↓
5. Deploy
   ↓
6. Monitor Logs
```

---

## Características de Depuración

### Available Debugging Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `get_service_logs` | Get service logs | Debug issues |
| `inspect_service` | Get service details | View configuration |
| `get_system_stats` | System monitoring | Check resources |
| `get_service_stats` | Service metrics | Performance data |

### Debugging with AI

#### Example 1: Service Not Starting

```
User: "My API service won't start, what's wrong?"

AI: 🔍 Inspecting service...
    📊 Checking logs...
    
    ❌ Error found:
    - Port 3000 already in use
    - Another service is using this port
    
    💡 Solution:
    Would you like me to:
    1. Change the port to 3001?
    2. Stop the conflicting service?
```

#### Example 2: Database Connection Failed

```
User: "My app can't connect to the database"

AI: 🔍 Checking configuration...
    📊 Testing connection...
    
    ❌ Error: Connection refused
    🔍 Root cause: DATABASE_URL is incorrect
    
    Current: postgres://localhost:5432/db
    Should be: postgres://postgres-db:5432/db
    
    💡 Fix: Update DATABASE_URL environment variable?
```

#### Example 3: High Memory Usage

```
User: "Is my service running okay?"

AI: 📊 Checking system stats...
    
    ⚠️ Warning detected:
    - Memory usage: 95% (1.9GB / 2GB)
    - CPU usage: 45%
    
    💡 Recommendations:
    1. Increase memory limit to 4GB
    2. Check for memory leaks
    3. Enable horizontal scaling
    
    Would you like me to increase resources?
```

### Log Analysis

```
User: "Show me the last 100 lines of logs for my-api"

AI: 📜 Retrieving logs...

    2026-03-14 10:30:15 INFO  Starting API server...
    2026-03-14 10:30:16 INFO  Connected to database
    2026-03-14 10:30:17 INFO  Server listening on port 8080
    2026-03-14 10:31:00 ERROR Request timeout for /api/users
    2026-03-14 10:31:01 WARN  High latency detected
    
    🔍 Analysis:
    - 2 errors in last hour
    - Timeout issues on /api/users endpoint
    - Possible database performance issue
```

---

## Características de Escalado

### Scaling Options in EasyPanel

| Type | Description | Status |
|------|-------------|--------|
| **Vertical Scaling** | Increase CPU/Memory | ✅ Available |
| **Horizontal Scaling** | Multiple replicas | ⚠️ Via Service Config |
| **Auto-Scaling** | Scale based on metrics | ⚠️ Manual trigger |

### Vertical Scaling (Resources)

```
User: "My service needs more resources, scale it up"

AI: 📊 Current resources:
    - CPU: 1 core
    - Memory: 2GB
    
    📈 Scaling up to:
    - CPU: 2 cores
    - Memory: 4GB
    
    ✅ Resources updated!
    🔄 Service restarting with new limits...
```

### Horizontal Scaling (Replicas)

```
User: "I need 3 replicas of my-api service"

AI: 📊 Current replicas: 1
    📈 Scaling to: 3 replicas
    
    ✅ Replica 1: Running
    ✅ Replica 2: Running
    ✅ Replica 3: Running
    
    🔄 Load balancer configured
```

### Monitoring-Based Scaling

```
User: "Check if my service needs scaling"

AI: 📊 Analyzing metrics...
    
    Current usage (last 24h):
    - CPU: 85% average, 95% peak
    - Memory: 78% average, 92% peak
    - Requests: 1000/min average
    
    ⚠️ Recommendation: Scale up
    
    Proposed configuration:
    - CPU: 2 → 4 cores
    - Memory: 4GB → 8GB
    
    Proceed with scaling?
```

### Manual Auto-Scaling Script

You can create automation scripts:

```python
# Example: Check and scale based on CPU usage
async def auto_scale():
    stats = await client.get_system_stats()
    cpu_usage = stats['cpuInfo']['usedPercentage']
    
    if cpu_usage > 80:
        print("⚠️ High CPU usage, scaling up...")
        await client.update_service(service_id, {
            "cpu": current_cpu * 2
        })
```

---

## Integración con IDEs (Antigravity/Cursor)

### What is Antigravity IDE?

**Antigravity** (also known as **Cursor** or similar AI-powered IDEs) is an AI-first code editor that can integrate with MCP servers to provide context-aware assistance.

### Can You Use EasyPanel MCP in Antigravity?

**Yes!** If Antigravity supports MCP (like Cursor, Cline, and other AI IDEs), you can use EasyPanel MCP.

### Configuration for Antigravity/Cursor

#### Step 1: Find Config File

```bash
# macOS
~/Library/Application Support/Cursor/User/settings.json

# Windows
%APPDATA%\Cursor\User\settings.json

# Linux
~/.config/Cursor/User/settings.json
```

#### Step 2: Add MCP Configuration

```json
{
  "mcpServers": {
    "easypanel": {
      "command": "python",
      "args": ["/absolute/path/to/easypanel-mcp/src/server.py"],
      "cwd": "/absolute/path/to/easypanel-mcp",
      "env": {
        "EASYPANEL_URL": "https://your-easypanel.com",
        "EASYPANEL_API_KEY": "ep_live_xxxxxxxxxxxxx"
      }
    }
  }
}
```

#### Step 3: Reload IDE

- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
- Type "Reload Window"
- Press Enter

### Using EasyPanel MCP in Antigravity

#### Example Workflow: Fix and Deploy

```
User: "My production service is failing, check the logs and fix it"

AI (in Antigravity):
🔍 Connecting to EasyPanel...
📜 Retrieving logs for 'production-api'...

Analysis:
- Error: OutOfMemoryException
- Memory limit: 2GB
- Current usage: 1.98GB

💡 Solution found:
1. Increase memory to 4GB
2. Deploy updated version

Proceeding with fix...
✅ Memory updated: 2GB → 4GB
🚀 Service redeployed
✅ Service is now healthy!
```

#### Example: GitHub Fix and Deploy

```
User: "Fix the bug in my GitHub repo and deploy"

AI:
📥 Cloning repository...
🔍 Analyzing code...
🐛 Bug found: Missing error handling in api/users.js

Fixing...
✅ Applied fix: Added try-catch block
📝 Committing changes...
🚀 Deploying to production...
✅ Deployment successful!
```

---

## Resolución de Problemas y Despliegues de Git

### Workflow: Fix Problem → Commit → Deploy

#### Scenario: Production Bug

```
1. User reports issue
   ↓
2. AI checks logs via MCP
   ↓
3. AI identifies root cause
   ↓
4. AI fixes code (in IDE)
   ↓
5. AI commits to GitHub
   ↓
6. AI deploys via MCP
   ↓
7. Issue resolved!
```

### Example: Complete Fix Flow

```
User: "Users can't login, fix it and deploy"

AI (using MCP + Git):
🔍 Checking service logs...
❌ Error found: Authentication service returning 500

📥 Cloning repository...
🔍 Analyzing auth.js...
🐛 Bug found: Missing environment variable

💻 Applying fix...
✅ Added missing env check
✅ Committed: "fix: Add missing env validation in auth"

🚀 Deploying to production...
✅ Build successful
✅ Deployment complete

🧪 Testing login...
✅ Login working!

Summary:
- Root cause: Missing env validation
- Fix: Added validation + error handling
- Deployed: v1.2.3
- Status: ✅ Resolved
```

### GitHub Integration Setup

To enable GitHub deployments:

```
User: "Connect my GitHub repository"

AI:
🔗 Connecting to GitHub...
📁 Repository: youruser/yourapp
🔑 Generating deploy key...
✅ GitHub connected!

Configuration:
- Branch: main
- Auto-deploy: Enabled
- Build command: docker build
```

---

## Resumen de Disponibilidad de Características

| Feature | Available | Notes |
|---------|-----------|-------|
| **API Key Auth** | ✅ Yes | Recommended method |
| **Email/Password Auth** | ✅ Yes | Alternative |
| **Isolated Networks** | ✅ Yes | Via service config |
| **Service Deployment** | ✅ Yes | Multiple methods |
| **GitHub Deploy** | ✅ Yes | Via services.app.updateSourceGithub |
| **Git Deploy** | ✅ Yes | Via services.app.updateSourceGit |
| **Docker Image Deploy** | ✅ Yes | Via services.app.updateSourceImage |
| **Log Retrieval** | ⚠️ Limited | Via service inspection |
| **System Monitoring** | ✅ Yes | Full stats available |
| **Resource Scaling** | ✅ Yes | CPU/Memory |
| **Horizontal Scaling** | ⚠️ Via Config | Service configuration |
| **Auto-Scaling** | ⚠️ Manual | Script-based |
| **Domain Management** | ✅ Yes | Custom domains |
| **Port Management** | ✅ Yes | Expose/hide ports |
| **Environment Variables** | ✅ Yes | Secure management |
| **Basic Auth** | ✅ Yes | HTTP auth |
| **Service Restart** | ✅ Yes | Instant restart |
| **Service Start/Stop** | ✅ Yes | Control state |

---

## Resolución de Problemas (Troubleshooting)

### Feature Not Available

**Problem:** AI says a feature is not available

**Solution:**
1. Check if EasyPanel supports it natively
2. Some features require specific EasyPanel plans
3. Verify API permissions

### Network Isolation Not Working

**Problem:** Services are still accessible from internet

**Solution:**
1. Ensure no public ports are configured
2. Check service configuration
3. Verify project network settings

### Deployment Fails

**Problem:** Service won't deploy

**Common causes:**
- Invalid Docker image
- Missing environment variables
- Resource limits exceeded
- Network configuration error

**Solution:**
```
User: "Deployment failed, check why"

AI: 🔍 Analyzing deployment...
    ❌ Error: Image not found
    
    💡 Fix: Update image name to 'nginx:latest'
```

---

## Documentación Relacionada

- **[AI Agents Integration](../integration/ai-agents.md)** - Connect with Claude, Cursor, etc.
- **[Configuration Guide](../getting-started/configuration.md)** - Setup and configuration
- **[Tools Reference](../tools/overview.md)** - Available MCP tools
- **[Security Guide](../integration/security.md)** - Security best practices

---

<p align="center" markdown>
**🚀 Master advanced EasyPanel MCP features!** Deploy, scale, and debug with AI assistance.
</p>
