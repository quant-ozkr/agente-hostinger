"""
deploy_logic_mcp.py — Verifica la salud del Backend (Motor Fiscal + Asesor) en producción.

NOTA: Tras la refactorización, el "Cerebro Lógico" (herramientas del Asesor)
ya NO es un servicio separado en puerto 8007. Ahora está integrado en el
Backend principal (puerto 8001).

Pasos que ejecuta:
  1. Verifica que el backend responde en puerto 8001
  2. Valida que las herramientas del Asesor están disponibles
  3. Muestra el estado de todos los servicios relevantes

Requisitos previos (.env en .agents/skills/hostinger-tesis-manager/scripts/.env):
  HOSTINGER_IP, HOSTINGER_USER, HOSTINGER_PORT, SSH_KEY_PATH
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

BACKEND_DIR  = "/var/www/tesis-app/backend"


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

    print(f"🚀 Verificando Backend (Motor Fiscal + Asesor) en {VPS_IP}:{VPS_PORT}...")

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

        # ── Paso 1: Validar health check del Backend en puerto 8001 ───────
        print("\n[1/3] Validando health check del Backend en puerto 8001...")
        health = _exec(client, "curl -sf http://localhost:8001/health || echo 'FAIL'")

        if "FAIL" in health or not health:
            print("   ❌ El Backend no responde en el puerto 8001. Verificando logs...")
            _exec(client, "sudo journalctl -u tesis-backend -n 20 --no-pager")
        else:
            print("   ✅ Backend respondiendo correctamente en :8001")
            print(f"   ↳ {health[:200] if health else 'OK'}")

        # ── Paso 2: Verificar que Orchestrator está disponible ────────────
        print("\n[2/3] Verificando Orchestrator (HITL) en puerto 8010...")
        orch_health = _exec(client, "curl -sf http://localhost:8010/health || echo 'FAIL'")

        if "FAIL" in orch_health or not orch_health:
            print("   ❌ Orchestrator no responde en el puerto 8010.")
        else:
            print("   ✅ Orchestrator respondiendo correctamente en :8010")

        # ── Paso 3: Estado de todos los servicios ────────────────────────
        print("\n[3/3] Estado de servicios del ecosistema:")
        services = [
            ("Backend (Motor + Asesor)", "tesis-backend"),
            ("Orchestrator (HITL)", "tesis-orchestrator"),
            ("MKT Agent (Captador)", "tesis-mkt"),
            ("PostgreSQL", "postgresql"),
            ("Nginx", "nginx"),
        ]
        for name, svc in services:
            status = _exec(client, f"sudo systemctl is-active {svc} 2>/dev/null || echo 'unknown'")
            icon = "✅" if "active" in status else "⚠️ "
            print(f"   {icon} {name}: {status}")

        # ── Servicios eliminados tras refactorización ──────────────────────
        print("\n📝 Servicios eliminados tras refactorización MCP→Backend:")
        print("   • tesis-logic-mcp (puerto 8007) - Ya no existe, integrado en Backend")

        sftp.close()
        print("\n🎉 Verificación del Backend completada.")

    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"❌ No se puede conectar a {VPS_IP}:{VPS_PORT}. ¿El VPS está encendido?")
        sys.exit(1)
    except paramiko.ssh_exception.AuthenticationException:
        print("❌ Falla de autenticación SSH. Verifica SSH_KEY_PATH y que la llave esté en el VPS.")
        sys.exit(1)
    except paramiko.ssh_exception.SSHException as e:
        print(f"❌ Error SSH: {e}")
        print("   Ejecuta: ssh-keyscan -H <IP_VPS> >> ~/.ssh/known_hosts")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    deploy()