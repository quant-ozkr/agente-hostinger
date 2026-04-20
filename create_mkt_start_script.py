import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cat <<'SCRIPT' > /var/www/agencia-mkt/start.sh
#!/bin/bash
set -e
cd /var/www/agencia-mkt
source venv/bin/activate
echo "[STARTUP] Starting uvicorn for Agencia MKT..."
exec uvicorn webhook_server:app \
    --host 127.0.0.1 \
    --port 8002 \
    --workers 2 \
    --log-level info
SCRIPT
chmod +x /var/www/agencia-mkt/start.sh
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
