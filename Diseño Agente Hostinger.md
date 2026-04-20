# **🤖 Diseño Integral del Agente DevOps para Hostinger VPS (Proyecto Tesis)**

Este documento detalla la arquitectura, habilidades (Skills), herramientas (Tools) vía MCP y los scripts necesarios para desplegar un agente de IA capaz de gestionar migraciones, mantenimiento y monitoreo en tu VPS de Hostinger, actuando como el reemplazo operativo del dashboard de Railway.

El diseño sigue las mejores prácticas de **AgentSkills.io** (divulgación progresiva, reglas encapsuladas) y utiliza **FastMCP (Python)** para interacciones seguras mediante SSH.

## **1\. Arquitectura del Sistema**

La solución se divide en tres capas principales:

1. **Capa de IA (El Agente):** Cliente MCP (ej. Claude Desktop, CLI de Gemini u OpenCode).  
2. **Capa de Contexto (AgentSkills):** Archivos .md que instruyen al agente sobre *cómo* y *cuándo* usar las herramientas, enfocados en tu stack: FastAPI, React, PostgreSQL y Nginx.  
3. **Capa de Ejecución (Servidor MCP):** Un script en Python aislado que expone funciones (Tools) al agente para conectarse al VPS de Hostinger vía SSH por el puerto 2222\.

### **Estructura de Directorios del Proyecto**

.agents/  
└── skills/  
    └── hostinger-tesis-manager/  
        ├── SKILL.md                 \# Contexto y reglas del agente  
        └── scripts/  
            ├── hostinger\_mcp.py     \# Servidor FastMCP (Las "Tools")  
            ├── setup\_env.sh         \# Script de preparación del entorno  
            └── .env                 \# Variables de entorno (NO subido a Git)

## **2\. Definición de la Habilidad: SKILL.md**

Este archivo debe guardarse en .agents/skills/hostinger-tesis-manager/SKILL.md. Contiene el "cerebro" del agente ajustado a tu plan de migración.

\---  
name: hostinger-tesis-manager  
description: Activa esta habilidad cuando el usuario necesite migrar, desplegar, mantener, depurar o monitorear la aplicación de la tesis (FastAPI/React) alojada en el VPS de Hostinger.  
compatibility: Requiere Python 3.10+, paramiko, FastMCP SDK y llaves SSH configuradas en el entorno local apuntando al puerto 2222\.  
metadata:  
  version: "1.1"  
  domain: "DevOps & Infrastructure"  
\---

\# Reglas de Gestión para Hostinger VPS (Tesis-App)

Actúas como un Ingeniero DevOps Senior administrando un VPS en Hostinger. Tu objetivo es reducir a cero el "Esfuerzo operativo" del usuario, reemplazando la conveniencia que proveía Railway.

\#\# Principios Básicos (CRÍTICOS)

1\.  \*\*Arquitectura Conocida:\*\* La aplicación vive en \`/var/www/tesis-app/\`. El backend (FastAPI/uvicorn) corre en el puerto 8001 controlado por \`tesis-backend.service\`. Nginx actúa como reverse proxy.  
2\.  \*\*Zero-Downtime y Fallback:\*\* Si un despliegue falla críticamente, recuerda al usuario que puede hacer \*rollback\* cambiando el registro DNS de vuelta a la URL de Railway.  
3\.  \*\*Confirmación de Usuario (Dry-Run):\*\* Si vas a ejecutar una acción destructiva (ej. borrar backups en \`/backups/postgres\` o reiniciar la DB), \*\*DEBES pedir confirmación explícita\*\*.  
4\.  \*\*No sobrescribas \`.env\`:\*\* El archivo \`/var/www/tesis-app/backend/.env\` es sagrado. Nunca lo modifiques ni lo expongas en texto plano completo.

\#\# Flujos de Trabajo Operativos

\#\#\# A. CI/CD y Despliegues  
\- El despliegue automatizado lo hace GitHub Actions usando \`/var/www/tesis-app/deploy.sh\`.   
\- Si el usuario pide un despliegue manual o revisar por qué falló un push, usa \`ejecutar\_script\_deploy\` para correr el script o leer \`/var/log/tesis-deploy.log\`.  
\- Después de cada despliegue, verifica que \`tesis-backend.service\` esté "active (running)".

\#\#\# B. Monitoreo y Depuración  
\- \*\*Errores 502/504 en la web:\*\* Verifica primero si \`uvicorn\` está corriendo usando \`verificar\_servicio\`. Si está corriendo, revisa \`/var/log/nginx/error.log\`.  
\- \*\*Errores de IA/Base de datos:\*\* Revisa los logs de FastAPI a través de systemd (\`journalctl \-u tesis-backend\`).  
\- Alerta al usuario si el espacio en disco (\`verificar\_estado\_servidor\`) es menor al 20%, ya que ChromaDB y los backups diarios de PostgreSQL consumen espacio rápido.

\#\#\# C. Mantenimiento Preventivo  
\- Si se requiere verificar la integridad de la base de datos tras la migración, ejecuta \`scripts/verify\_schema.py\` dentro del entorno virtual del backend.

## **3\. Servidor MCP y Herramientas (Tools)**

Guarda este código en .agents/skills/hostinger-tesis-manager/scripts/hostinger\_mcp.py. Se han adaptado los comandos para tu puerto SSH 2222 y tu usuario tesis.

\# hostinger\_mcp.py  
import os  
import paramiko  
from mcp.server.fastmcp import FastMCP  
from dotenv import load\_dotenv

load\_dotenv()

mcp \= FastMCP("HostingerDevOpsTesis")

def ejecutar\_comando\_ssh(comando: str) \-\> str:  
    """Ejecuta un comando SSH en el VPS. Adaptado para puerto 2222 y llaves."""  
    ip \= os.getenv("HOSTINGER\_IP")  
    usuario \= os.getenv("HOSTINGER\_USER", "tesis")  
    puerto \= int(os.getenv("HOSTINGER\_PORT", 2222))  
    llave\_ruta \= os.getenv("SSH\_KEY\_PATH")

    if not all(\[ip, usuario, llave\_ruta\]):  
        return "Error: Faltan variables de entorno."

    cliente \= paramiko.SSHClient()  
    cliente.set\_missing\_host\_key\_policy(paramiko.AutoAddPolicy())  
      
    try:  
        cliente.connect(ip, port=puerto, username=usuario, key\_filename=llave\_ruta)  
        stdin, stdout, stderr \= cliente.exec\_command(comando)  
        exit\_status \= stdout.channel.recv\_exit\_status()  
          
        salida \= stdout.read().decode('utf-8').strip()  
        error \= stderr.read().decode('utf-8').strip()  
          
        if exit\_status \!= 0:  
            return f"Error \[{exit\_status}\]: {error}\\nSalida parcial: {salida}"  
        return salida if salida else "Comando ejecutado con éxito."  
    except Exception as e:  
        return f"Excepción SSH: {str(e)}"  
    finally:  
        cliente.close()

@mcp.tool()  
def verificar\_estado\_servidor() \-\> str:  
    """Verifica CPU, RAM y uso de disco. Especial atención al directorio de backups y ChromaDB."""  
    comando \= """  
    echo "--- MEMORIA \---" && free \-h && \\  
    echo "--- DISCO TOTAL \---" && df \-h / && \\  
    echo "--- DISCO BACKUPS \---" && du \-sh /backups/postgres 2\>/dev/null || echo 'No backups dir' && \\  
    echo "--- DISCO CHROMADB \---" && du \-sh /var/www/tesis-app/backend/data/chroma\_db 2\>/dev/null || echo 'No chroma dir' && \\  
    echo "--- CARGA \---" && uptime  
    """  
    return ejecutar\_comando\_ssh(comando)

@mcp.tool()  
def verificar\_servicio(nombre\_servicio: str \= "tesis-backend") \-\> str:  
    """  
    Comprueba el estado de un servicio systemd (ej. tesis-backend, nginx, postgresql).  
    Útil para saber si uvicorn o nginx se cayeron.  
    """  
    comando \= f"systemctl status {nombre\_servicio} \--no-pager | head \-n 15"  
    return ejecutar\_comando\_ssh(comando)

@mcp.tool()  
def ejecutar\_script\_deploy() \-\> str:  
    """  
    Ejecuta el script de despliegue oficial (deploy.sh) que simula el proceso de CI/CD.  
    Hace git pull, actualiza dependencias y reinicia systemd.  
    """  
    comando \= "sudo /var/www/tesis-app/deploy.sh"  
    return ejecutar\_comando\_ssh(comando)

@mcp.tool()  
def leer\_logs\_app(fuente: str \= "backend", lineas: int \= 50\) \-\> str:  
    """  
    Lee logs de la aplicación.  
    fuente puede ser: 'backend' (journalctl uvicorn), 'nginx\_error', 'deploy'.  
    """  
    if fuente \== "backend":  
        comando \= f"journalctl \-u tesis-backend \-n {lineas} \--no-pager"  
    elif fuente \== "nginx\_error":  
        comando \= f"sudo tail \-n {lineas} /var/log/nginx/error.log"  
    elif fuente \== "deploy":  
        comando \= f"tail \-n {lineas} /var/log/tesis-deploy.log"  
    else:  
        return "Fuente no válida. Usa 'backend', 'nginx\_error' o 'deploy'."  
      
    return ejecutar\_comando\_ssh(comando)

@mcp.tool()  
def ejecutar\_script\_mantenimiento(script: str) \-\> str:  
    """  
    Ejecuta scripts Python dentro del entorno virtual.  
    Útil para 'scripts/verify\_schema.py' o 'scripts/ensure\_alembic.py'.  
    """  
    comando \= f"""  
    cd /var/www/tesis-app/backend  
    source venv/bin/activate  
    python scripts/{script}  
    """  
    return ejecutar\_comando\_ssh(comando)

if \_\_name\_\_ \== "\_\_main\_\_":  
    mcp.run()

## **4\. Scripts de Configuración y Entorno**

Guarda este script en .agents/skills/hostinger-tesis-manager/scripts/setup\_env.sh.

\#\!/bin/bash  
echo "⚙️ Configurando entorno para Agente VPS Tesis..."

if \[ \! \-d ".venv" \]; then  
    python3 \-m venv .venv  
fi

source .venv/bin/activate  
pip install \--upgrade pip  
pip install mcp paramiko python-dotenv

if \[ \! \-f ".env" \]; then  
    cat \<\<EOT \> .env  
HOSTINGER\_IP=tu\_ip\_del\_vps  
HOSTINGER\_PORT=2222  
HOSTINGER\_USER=tesis  
SSH\_KEY\_PATH=/ruta/a/tu/.ssh/id\_rsa  
EOT  
    echo "⚠️ Archivo .env creado. Por favor, configúralo."  
fi  
echo "🚀 Terminado."

## **5\. Integración del Cliente (Configuración MCP)**

Añade esto a la configuración de tu cliente de IA local (ej. claude\_desktop\_config.json):

{  
  "mcpServers": {  
    "hostinger-tesis-manager": {  
      "command": "/ruta/absoluta/.agents/skills/hostinger-tesis-manager/scripts/.venv/bin/python",  
      "args": \[  
        "/ruta/absoluta/.agents/skills/hostinger-tesis-manager/scripts/hostinger\_mcp.py"  
      \]  
    }  
  }  
}  
