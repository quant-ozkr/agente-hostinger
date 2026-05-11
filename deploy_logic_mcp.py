"""
deploy_logic_mcp.py — Despliega el Cerebro Lógico MCP en el VPS de producción.

Pasos que ejecuta:
  1. Sube el archivo del servicio systemd (tesis-logic-mcp.service) al VPS
  2. Activa e inicia el servicio en systemd
  3. Añade MCP_API_KEY al .env del backend si no está presente
  4. Reinicia el backend para que tome la nueva variable
  5. Valida el health check en el puerto 8007

Requisitos previos (.env en .agents/skills/hostinger-tesis-manager/scripts/.env):
  HOSTINGER_IP, HOSTINGER_USER, HOSTINGER_PORT, SSH_KEY_PATH, MCP_API_KEY
"""

import os
import sys
import paramiko
from dotenv import load_dotenv

# Forzar salida UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Cargar .env con credenciales SSH ─────────────────────────────────────────
env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

VPS_IP       = os.getenv("HOSTINGER_IP")
VPS_USER     = os.getenv("HOSTINGER_USER")
VPS_PORT     = int(os.getenv("HOSTINGER_PORT", "22"))
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
MCP_API_KEY  = os.getenv("MCP_API_KEY", "")

BACKEND_DIR  = "/var/www/tesis-app/backend"
SERVICE_NAME = "tesis-logic-mcp"
# Ruta al .service relativa a este script (inf-expert-agent/../liq-expert-agent/...)
_HERE = os.path.dirname(os.path.abspath(__file__))
SERVICE_FILE = os.path.join(_HERE, "..", "liq-expert-agent", "backend", "infra", "tesis-logic-mcp.service")
SERVICE_FILE = os.path.normpath(SERVICE_FILE)


def _exec(client: paramiko.SSHClient, cmd: str, check: bool = True) -> str:
    """Ejecuta un comando SSH y retorna stdout. Muestra stderr si hay error."""
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"   ↳ {out[:400]}")
    if err:
        print(f"   ⚠  {err[:200]}")
    return out


def deploy():
    if not all([VPS_IP, VPS_USER, SSH_KEY_PATH]):
        print("❌ Faltan variables de entorno SSH (HOSTINGER_IP, HOSTINGER_USER, SSH_KEY_PATH).")
        print(f"   Buscando en: {env_path}")
        sys.exit(1)

    if not os.path.exists(SERVICE_FILE):
        print(f"❌ Archivo de servicio no encontrado: {SERVICE_FILE}")
        sys.exit(1)

    print(f"🚀 Desplegando Cerebro Lógico MCP en {VPS_IP}:{VPS_PORT}...")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(
            hostname=VPS_IP, port=VPS_PORT,
            username=VPS_USER, key_filename=SSH_KEY_PATH,
            timeout=15, look_for_keys=False, allow_agent=False
        )
        sftp = client.open_sftp()

        # ── Paso 1: Subir el archivo del servicio ─────────────────────────
        print("\n[1/5] Subiendo tesis-logic-mcp.service...")
        sftp.put(SERVICE_FILE, "/tmp/tesis-logic-mcp.service")
        print("   ✅ Archivo subido a /tmp/")

        # ── Paso 2: Instalar y activar el servicio ────────────────────────
        print("\n[2/5] Instalando y activando el servicio systemd...")
        cmds_systemd = [
            "sudo mv /tmp/tesis-logic-mcp.service /etc/systemd/system/tesis-logic-mcp.service",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable tesis-logic-mcp",
            "sudo systemctl restart tesis-logic-mcp",
        ]
        for cmd in cmds_systemd:
            print(f"   $ {cmd}")
            _exec(client, cmd)
        print("   ✅ Servicio configurado e iniciado")

        # ── Paso 3: Añadir MCP_API_KEY al .env del backend ───────────────
        print("\n[3/5] Verificando MCP_API_KEY en el .env del backend...")
        env_file = f"{BACKEND_DIR}/.env"
        check_cmd = f"grep -c 'MCP_API_KEY' {env_file} 2>/dev/null || echo 0"
        count = _exec(client, check_cmd).strip()

        if count == "0":
            if MCP_API_KEY:
                add_cmd = f"echo 'MCP_API_KEY={MCP_API_KEY}' | sudo tee -a {env_file}"
                _exec(client, add_cmd)
                print("   ✅ MCP_API_KEY añadida al .env del backend")
            else:
                print("   ⚠  MCP_API_KEY no está en el .env local. Añádela manualmente al VPS.")
        else:
            print("   ✅ MCP_API_KEY ya existe en el .env del backend")

        # ── Paso 4: Reiniciar el backend para tomar la nueva variable ─────
        print("\n[4/5] Reiniciando tesis-backend para tomar nuevas variables...")
        _exec(client, "sudo systemctl restart tesis-backend")
        import time; time.sleep(3)
        status = _exec(client, "sudo systemctl is-active tesis-backend")
        if "active" in status:
            print("   ✅ Backend reiniciado correctamente")
        else:
            print(f"   ⚠  Estado del backend: {status}")

        # ── Paso 5: Validar health check del MCP en puerto 8007 ──────────
        print("\n[5/5] Validando health check en puerto 8007...")
        import time; time.sleep(5)  # Dar tiempo al servicio para arrancar
        health = _exec(client, "curl -sf http://localhost:8007/health || echo 'FAIL'")

        if "FAIL" in health or not health:
            print("   ❌ El MCP no responde en el puerto 8007. Verificando logs...")
            logs = _exec(client, f"sudo journalctl -u {SERVICE_NAME} -n 20 --no-pager")
        else:
            print("   ✅ Cerebro Lógico MCP respondiendo correctamente en :8007")

        # ── Resumen del estado de todos los servicios ─────────────────────
        print("\n📊 Estado de todos los servicios del ecosistema:")
        services = ["tesis-backend", "tesis-brainstem", SERVICE_NAME, "nginx"]
        for svc in services:
            status = _exec(client, f"sudo systemctl is-active {svc} 2>/dev/null")
            icon = "✅" if "active" in status else "❌"
            print(f"   {icon} {svc}: {status}")

        sftp.close()
        print("\n🎉 Despliegue del Cerebro Lógico MCP completado exitosamente.")

    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"❌ No se puede conectar a {VPS_IP}:{VPS_PORT}. ¿El VPS está encendido?")
        sys.exit(1)
    except paramiko.ssh_exception.AuthenticationException:
        print("❌ Falla de autenticación SSH. Verifica SSH_KEY_PATH y que la llave esté en el VPS.")
        sys.exit(1)
    except paramiko.ssh_exception.SSHException as e:
        print(f"❌ Error SSH (posible host no reconocido - RejectPolicy activa): {e}")
        print("   Ejecuta: ssh-keyscan -H <IP_VPS> >> ~/.ssh/known_hosts")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    deploy()
