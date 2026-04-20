import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cat <<'SCRIPT' > /var/www/tesis-staging/backend/start.sh
#!/bin/bash
set -e
cd /var/www/tesis-staging/backend
source venv/bin/activate
echo "[STARTUP] Starting uvicorn for STAGING..."
exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8003 \
    --workers 2 \
    --log-level info
SCRIPT
chmod +x /var/www/tesis-staging/backend/start.sh
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
