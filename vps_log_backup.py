import os
import paramiko
from dotenv import load_dotenv

env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

def ejecutar_comando_ssh(comando):
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto = int(os.getenv("HOSTINGER_PORT", 22))
    llave_ruta = os.getenv("SSH_KEY_PATH")
    
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        stdin, stdout, stderr = cliente.exec_command(comando)
        exit_status = stdout.channel.recv_exit_status()
        salida = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return exit_status, salida, error
    except Exception as e:
        return -1, "", str(e)
    finally:
        cliente.close()

def setup_log_backup():
    print("--- FASE 4: LOG ROTATION Y BACKUPS ---")
    
    # 1. Logrotate para tesis
    print("Configurando logrotate...")
    logrotate_conf = """/var/www/tesis-app/backend/logs/*.jsonl {
    weekly
    rotate 12
    compress
    missingok
    notifempty
    create 0644 tesis tesis
    copytruncate
}

/var/log/tesis-deploy.log {
    monthly
    rotate 6
    compress
    missingok
    notifempty
    create 0644 tesis tesis
}
"""
    cmd_rotate = f"printf '{logrotate_conf}' | sudo tee /etc/logrotate.d/tesis > /dev/null"
    status, out, err = ejecutar_comando_ssh(cmd_rotate)
    if status == 0:
        print("✔ Configuración de logrotate creada.")
    else:
        print(f"✘ Error en logrotate: {err}")

    # 2. Backups de base de datos
    print("\nConfigurando backups automáticos...")
    # Crear directorio si no existe
    ejecutar_comando_ssh("sudo mkdir -p /backups/postgres && sudo chown tesis:tesis /backups/postgres")
    
    # Crontab: diario 3 AM backup, 4 AM cleanup
    # Nota: pg_dump necesitará que el usuario 'tesis' tenga acceso o usar un .pgpass
    # Asumimos que podemos usar sudo -u postgres o que el usuario de la DB está configurado
    # En el VPS el usuario es 'rootAdminLiq', debemos usarlo en el comando.
    
    cron_jobs = """# Backups LiqExpert
0 3 * * * pg_dump -U rootAdminLiq liqExpert | gzip > /backups/postgres/liqExpert_$(date +\\%Y\\%m\\%d_\\%H\\%M).sql.gz
0 4 * * * find /backups/postgres -name "*.sql.gz" -mtime +30 -delete
"""
    # Para que pg_dump no pida password, debemos crear un .pgpass
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")
    
    pgpass_line = f"{db_host}:5432:{db_name}:{db_user}:{db_pass}"
    ejecutar_comando_ssh(f"echo '{pgpass_line}' > ~/.pgpass && chmod 600 ~/.pgpass")
    
    # Instalar crontab usando un archivo temporal para evitar problemas con printf
    cmd_cron = f"echo '{cron_jobs}' > /tmp/mycron && crontab /tmp/mycron && rm /tmp/mycron"
    status, out, err = ejecutar_comando_ssh(cmd_cron)
    if status == 0:
        print("✔ Crontab actualizado.")
    else:
        print(f"✘ Error al actualizar crontab: {err}")

    status, out, err = ejecutar_comando_ssh("crontab -l")
    print("\nCrontab actual:")
    print(out)

if __name__ == "__main__":
    setup_log_backup()
