# EasyPanel MCP Server

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green?logo=anthropic&logoColor=white)](https://modelcontextprotocol.io/)
[![EasyPanel Compatible](https://img.shields.io/badge/EasyPanel-Compatible-orange?logo=docker&logoColor=white)](https://easypanel.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

Servidor de **Model Context Protocol (MCP)** para **EasyPanel**. Este conector permite a clientes de inteligencia artificial y entornos de automatización gestionar infraestructura, desplegar servicios, configurar redes y monitorear recursos mediante la API tRPC de EasyPanel en lenguaje natural.

---

## Descripción General

Este servidor implementa el estándar abierto **Model Context Protocol (MCP)** desarrollado por Anthropic para ofrecer herramientas de DevOps automatizadas. Permite a agentes de IA interactuar directamente con tu instancia de EasyPanel de forma local y segura, automatizando tareas complejas de administración de servidores, despliegues y diagnósticos.

### Características Principales

*   **Gestión Completa de Servicios:** Listado, inspección, creación, actualización, detención y reinicio de aplicaciones y bases de datos.
*   **Manejo Inteligente de Recursos:** Detección automática y ruteo de namespaces tRPC según el tipo de servicio (`app`, `postgres`, `redis`, `mysql`, `mongodb`, `mariadb`).
*   **Auto-Scaling Automatizado:** Escalado vertical de CPU y memoria basado en métricas y límites definidos.
*   **Análisis y Debugging:** Recuperación de logs estructurados e información de despliegue para auditoría y diagnóstico de fallos en tiempo real.
*   **Descubrimiento de Redes:** Análisis automático de topologías de comunicación interna y pública de Docker.
*   **Soporte Multicliente:** Diseñado tanto para transporte local de flujo estándar (`stdio`) como para conexión remota vía Server-Sent Events (`sse`/`http`).

---

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/dannymaaz/easypanel-mcp
cd easypanel-mcp
```

### 2. Configurar el entorno virtual e instalar
Recomendamos usar un entorno virtual para aislar las dependencias:

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**En macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto basándote en el ejemplo provisto:
```bash
cp .env.example .env
```

Edita el archivo `.env` configurando los accesos a tu EasyPanel:
```env
# URL de acceso a tu instancia (ej. https://panel.tudominio.com)
EASYPANEL_URL=https://tu-easypanel.com

# Token de API o credenciales en formato email:password
EASYPANEL_API_KEY=tu_api_key_aqui

# Parámetros adicionales
EASYPANEL_TIMEOUT=30
EASYPANEL_VERIFY_SSL=true

# Configuración del servidor MCP
MCP_HOST=127.0.0.1
MCP_PORT=8080
MCP_LOG_LEVEL=INFO
```

---

## Configuración en Clientes MCP

### 1. Antigravity IDE
Para integrar el servidor en **Antigravity**, añade la ruta del script en la configuración del gestor de plugins de MCP.

Asegúrate de apuntar al ejecutable de Python de tu entorno virtual (`venv`) para que localice las dependencias instaladas:

```json
{
  "mcpServers": {
    "easypanel-mcp": {
      "command": "C:\\ruta\\a\\easypanel-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\ruta\\a\\easypanel-mcp\\src\\server.py"],
      "env": {
        "EASYPANEL_URL": "https://tu-easypanel.com",
        "EASYPANEL_API_KEY": "tu_api_key"
      }
    }
  }
}
```

### 2. Cursor / VS Code (Extensiones Cline & Roo Code)
En editores compatibles con OpenCode o extensiones de agentes inteligentes:

1.  Abre el panel de configuración de la extensión (ej. en **Roo Code**, ve a *Settings* > *MCP Servers*).
2.  Añade una nueva configuración de servidor:
    *   **Name:** `easypanel`
    *   **Type:** `command`
    *   **Command:** `python` (o la ruta al ejecutable de tu `venv`)
    *   **Args:** `["/ruta/absoluta/a/easypanel-mcp/src/server.py"]`
    *   **Environment Variables:**
        *   `EASYPANEL_URL`: `https://tu-easypanel.com`
        *   `EASYPANEL_API_KEY`: `tu_api_key`

### 3. Claude Desktop
Añade el servidor al archivo de configuración de Claude Desktop (`claude_desktop_config.json`):

**En Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**En macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "easypanel-mcp": {
      "command": "python",
      "args": ["/ruta/absoluta/a/easypanel-mcp/src/server.py"],
      "env": {
        "EASYPANEL_URL": "https://tu-easypanel.com",
        "EASYPANEL_API_KEY": "tu_api_key"
      }
    }
  }
}
```

### 4. n8n (Integración remota vía SSE)
Si deseas desplegarlo de forma dedicada como servicio remoto, inicia el servidor en modo HTTP:
```bash
python src/server.py http
```

Esto levantará el servidor en `http://127.0.0.1:8080` utilizando Server-Sent Events (SSE). Puedes integrarlo en nodos HTTP de n8n o sistemas externos realizando peticiones estructuradas al endpoint de herramientas:

*   **Endpoint:** `http://localhost:8080/mcp`
*   **Formato de petición:**
    ```json
    {
      "method": "tools/call",
      "params": {
        "name": "list_services",
        "arguments": {
          "project_id": "mi-proyecto"
        }
      }
    }
    ```

---

## Ejemplos Prácticos de Uso

Una vez conectado, puedes interactuar directamente con tu agente haciéndole peticiones de infraestructura basadas en la vida real:

### Despliegue de Aplicaciones
> **Usuario:** "Despliega un servicio frontend usando la imagen nginx:alpine en el proyecto principal."  
> **IA (Interno):** Invoca `create_service(name="frontend", project_id="principal", image="nginx:alpine")` y posteriormente `deploy_service`.  
> **IA (Respuesta):** *"He creado y desplegado el servicio 'frontend' exitosamente en tu proyecto. Está listo para recibir configuración de dominio."*

### Diagnóstico de Caídas
> **Usuario:** "¿Por qué el servicio backend está fallando?"  
> **IA (Interno):** Invoca `get_service_logs(service_id="backend")`.  
> **IA (Respuesta):** *"El servicio backend reporta un estado 'crashed' debido al siguiente error en consola: 'ConnectionRefusedError: No se pudo establecer conexión con redis-cache en el puerto 6379'. ¿Deseas que verifique si el contenedor de Redis está detenido?"*

### Monitoreo y Escalado
> **Usuario:** "Verifica las estadísticas del sistema y escala el servicio backend si el uso de CPU es alto."  
> **IA (Interno):** Invoca `get_system_stats()` seguido de `scale_service(service_id="backend", cpu=2, memory=4096)`.

---

## Herramientas Disponibles

| Categoría | Herramienta | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| **Servicios** | `list_services` | `project_id` (opcional) | Lista todos los servicios y sus estados. |
| | `get_service` | `service_id` (requerido) | Obtiene la configuración detallada de un servicio. |
| | `create_service` | `name`, `project_id`, `image`, `config` | Crea un nuevo servicio (soporta apps y DBs). |
| | `update_service` | `service_id`, `config` | Modifica configuraciones de entorno, puertos y recursos. |
| | `delete_service` | `service_id` | Remueve un servicio de EasyPanel. |
| | `restart_service` | `service_id` | Reinicia de inmediato el contenedor de la aplicación. |
| | `get_service_logs` | `service_id`, `lines` (opcional) | Obtiene los últimos logs de consola del contenedor. |
| **Despliegues** | `list_deployments`| `project_id` (opcional) | Lista el historial de despliegues. |
| | `create_deployment`| `project_id`, `service_id`, `image` | Lanza un nuevo despliegue actualizando la imagen. |
| **Redes** | `list_networks` | - | Descubre la topología de red Docker pública/interna. |
| **Proyectos** | `list_projects` | - | Lista los proyectos creados en la instancia. |
| | `create_project` | `name`, `description` (opcional) | Crea un nuevo proyecto organizador. |
| **Monitoreo** | `get_system_stats`| - | Obtiene estadísticas en tiempo real de CPU, RAM y disco. |
| **Escalado** | `scale_service` | `service_id`, `cpu`, `memory` | Escala verticalmente los recursos asignados. |
| | `auto_scale_service`| `service_id`, `cpu_threshold`, `memory_threshold` | Escala dinámicamente según la carga actual. |
| **Seguridad** | `list_domains` | - | Lista los dominios asignados en la instancia. |
| | `get_public_key` | - | Obtiene la clave SSH pública para despliegues Git. |

---

## Verificación del Entorno

Para verificar la conectividad de la API y el estado de la configuración sin arrancar el servidor MCP completo, puedes ejecutar la suite de pruebas unitarias:

```bash
python -m pytest tests/test_basic.py -v
```

---

## Autor

*   **Danny Maaz** - [LinkedIn](https://linkedin.com/in/dannymaaz) • [GitHub](https://github.com/dannymaaz)

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
