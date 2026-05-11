"""
Skill: Sync DB Params
Exports local parameter tables, sanitizes them, and imports them into the VPS.
Handles common pitfalls like encoding, foreign keys, and truncating.
"""
import os
import subprocess
from core.ssh_utils import get_ssh_connection_from_env, logger

CFO_POSTGRES_CONTAINER = "cfo_postgres"
VPS_POSTGRES_CONTAINER = "cfo_postgres"


def sync_db_params(tables: list[str]) -> str:
    if not tables:
        return "Error: No tables specified for sync."

    local_sql = "temp_params_export.sql"
    fixed_sql = "temp_params_fixed.sql"
    remote_path = "/tmp/sync_params.sql"

    try:
        logger.info(f"Exporting local tables: {', '.join(tables)}")
        table_args = " ".join([f"-t {t}" for t in tables])
        cmd = f'docker exec -i {CFO_POSTGRES_CONTAINER} pg_dump -U agencia_user -d agencia_mkt_db --data-only --column-inserts {table_args}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=False)

        if result.returncode != 0:
            return f"Error exporting local data: {result.stderr.decode('utf-8')}"

        content = result.stdout.decode('utf-8', errors='ignore')
        content = content.replace("'430c6573-4c0d-46dc-8ccb-6f1260ecfc6f'", "NULL")

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

        logger.info("Importing data into VPS database...")
        import_cmd = f"docker exec -i {VPS_POSTGRES_CONTAINER} psql -U agencia_user -d agencia_mkt_db < {remote_path}"
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
    tables_to_sync = [
        "indices_inflacion", "tasas_historicas", "unidad_valor_tributario",
        "parametros_beneficios", "parametros_pricing", "parametros_renta",
        "reglas_interes", "tarifas_renta", "topes_deducciones"
    ]
    print(sync_db_params(tables_to_sync))
