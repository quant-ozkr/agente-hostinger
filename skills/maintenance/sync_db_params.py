"""
Skill: Sync DB Params v2.0
Exports local parameter tables, sanitizes them, and imports them into the VPS.
Architecture v2.0: Targets cfo-expert-agent-postgres-1 and liqExpert database.
"""
import os
import subprocess
from core.ssh_utils import get_ssh_connection_from_env, logger

CFO_POSTGRES_CONTAINER = "cfo-expert-agent-postgres-1"
VPS_POSTGRES_CONTAINER = "cfo-expert-agent-postgres-1"
DB_NAME = "liqExpert"
DB_USER = "rootAdminLiq"

def sync_db_params(tables: list[str]) -> str:
    if not tables:
        return "Error: No tables specified for sync."

    fixed_sql = "temp_params_fixed.sql"
    remote_path = "/tmp/sync_params.sql"

    try:
        logger.info(f"Exporting local tables from {CFO_POSTGRES_CONTAINER}...")
        table_args = " ".join([f"-t {t}" for t in tables])
        cmd = f'docker exec -i {CFO_POSTGRES_CONTAINER} pg_dump -U {DB_USER} -d {DB_NAME} --data-only --column-inserts {table_args}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=False)

        if result.returncode != 0:
            return f"Error exporting local data: {result.stderr.decode('utf-8')}"

        content = result.stdout.decode('utf-8', errors='ignore')
        
        # Sanitización de IDs específicos si es necesario
        # content = content.replace("'some-old-id'", "NULL")

        truncate_cmd = f"TRUNCATE TABLE {', '.join(tables)} CASCADE;\n"

        with open(fixed_sql, "w", encoding="utf-8") as f:
            f.write(truncate_cmd + content)

        conn = get_ssh_connection_from_env()
        if not conn:
            return "Error: Could not establish SSH connection (check .env)."

        logger.info(f"Uploading fixed SQL to VPS: {remote_path}")
        sftp = conn.client.open_sftp()
        sftp.put(fixed_sql, remote_path)
        sftp.close()

        logger.info(f"Importing data into VPS database {DB_NAME}...")
        import_cmd = f"docker exec -i {VPS_POSTGRES_CONTAINER} psql -U {DB_USER} -d {DB_NAME} < {remote_path}"
        status, out, err = conn.execute_command(import_cmd)

        conn.close()

        if os.path.exists(fixed_sql):
            os.remove(fixed_sql)

        if status == 0:
            return f"Sync successful for tables: {', '.join(tables)}\n{out}"
        else:
            return f"Sync failed during import:\nSTDOUT: {out}\nSTDERR: {err}"

    except Exception as e:
        logger.error(f"Critical error in sync_db_params: {e}")
        return f"Sync failed: {str(e)}"

if __name__ == "__main__":
    # Tablas maestras del Motor Tributario
    tables_to_sync = [
        "indices_inflacion", "tasas_historicas", "unidad_valor_tributario",
        "parametros_beneficios", "parametros_pricing", "parametros_renta",
        "reglas_interes", "tarifas_renta", "topes_deducciones"
    ]
    print(sync_db_params(tables_to_sync))
