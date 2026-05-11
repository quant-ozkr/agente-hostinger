"""
Skill: Pull DB Params (VPS -> Local)
Exports parametric tables from VPS database, downloads via SFTP, and imports into local Docker PostgreSQL.
Requires VPS SSH credentials configured in .env (HOSTINGER_IP, HOSTINGER_USER, SSH_KEY_PATH).

Prerequisitos:
  - Antes de ejecutar, hacer pg_dump de respaldo en el VPS:
      ssh tesis@<VPS_IP> "pg_dump -U rootAdminLiq liqExpert | gzip > /backups/postgres/pre_sync_$(date +%Y%m%d).sql.gz"
  - Tener el stack local levantado (docker-compose.platform-local.yml up -d)
  - Tener configuradas las variables SSH en .env del inf-expert-agent
"""
import os
import subprocess
from core.ssh_utils import get_ssh_connection_from_env, logger

LOCAL_POSTGRES_CONTAINER = "liqexpert_postgres"
VPS_POSTGRES_CONTAINER = "cfo_postgres"
LOCAL_DB_USER = "app"
LOCAL_DB_NAME = "liqexpert_dev"

# Lista completa de tablas parametricas
ALL_PARAM_TABLES = [
    "indices_inflacion",
    "tasas_historicas",
    "unidad_valor_tributario",
    "parametros_beneficios",
    "parametros_pricing",
    "parametros_renta",
    "reglas_interes",
    "tarifas_renta",
    "topes_deducciones",
    "codigos_direccion_seccional",
]


def pull_db_params(tables: list[str] = None) -> str:
    if not tables:
        tables = ALL_PARAM_TABLES

    remote_sql = "/tmp/param_export.sql"
    local_sql = "temp_params_from_vps.sql"

    try:
        # 1. Conectar al VPS via SSH
        conn = get_ssh_connection_from_env()
        if not conn:
            return (
                "Error: No se pudo establecer conexion SSH con el VPS.\n"
                "Verifica que las variables HOSTINGER_IP, HOSTINGER_USER y SSH_KEY_PATH "
                "esten configuradas en el .env del inf-expert-agent."
            )

        logger.info(f"Conectado al VPS. Exportando tablas: {', '.join(tables)}")

        # 2. Ejecutar pg_dump en el VPS para las tablas parametricas
        table_args = " ".join([f"-t {t}" for t in tables])
        dump_cmd = (
            f"docker exec {VPS_POSTGRES_CONTAINER} pg_dump "
            f"-U rootAdminLiq -d liqExpert "
            f"--data-only --column-inserts {table_args}"
        )
        logger.info(f"Ejecutando dump en VPS: {dump_cmd[:80]}...")
        status, out, err = conn.execute_command(dump_cmd)

        if status != 0:
            return f"Error exportando datos del VPS:\nSTDERR: {err}"

        # Guardar output en archivo local temporal
        with open(local_sql, "w", encoding="utf-8") as f:
            f.write(out)

        # 3. Subir el SQL al VPS (para que esté accesible)
        sftp = conn.client.open_sftp()
        sftp.put(local_sql, remote_sql)
        sftp.close()

        logger.info(f"Archivo SQL subido a VPS: {remote_sql}")

        # 4. Descargar el SQL desde el VPS a local via SFTP (ya lo tenemos en local_sql)

        # 5. Cerrar conexion VPS
        conn.close()

        # 6. Importar en la base de datos local via Docker
        logger.info("Importando datos en base de datos local...")

        # Primero truncar tablas existentes para evitar duplicados
        truncate_cmd = f"TRUNCATE TABLE {', '.join(tables)} CASCADE;"

        proc = subprocess.run(
            [
                "docker", "exec", "-i", LOCAL_POSTGRES_CONTAINER,
                "psql", "-U", LOCAL_DB_USER, "-d", LOCAL_DB_NAME,
            ],
            input=truncate_cmd,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            logger.warning(f"Truncate warning (puede que tablas no existan aun): {proc.stderr}")

        # Importar datos
        with open(local_sql, "r", encoding="utf-8") as f:
            sql_content = f.read()

        proc = subprocess.run(
            [
                "docker", "exec", "-i", LOCAL_POSTGRES_CONTAINER,
                "psql", "-U", LOCAL_DB_USER, "-d", LOCAL_DB_NAME,
            ],
            input=sql_content,
            capture_output=True,
            text=True,
        )

        # Limpiar archivo temporal
        if os.path.exists(local_sql):
            os.remove(local_sql)

        if proc.returncode == 0:
            return (
                f"Pull completado exitosamente para tablas: {', '.join(tables)}\n"
                f"{proc.stdout}"
            )
        else:
            return (
                f"Error durante importacion local:\n"
                f"STDOUT: {proc.stdout}\n"
                f"STDERR: {proc.stderr}"
            )

    except Exception as e:
        logger.error(f"Error critico en pull_db_params: {e}")
        return f"Pull fallo: {str(e)}"


if __name__ == "__main__":
    print(pull_db_params())
