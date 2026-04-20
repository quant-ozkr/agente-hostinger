import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/agencia-mkt
echo "--- REQUIREMENTS ---"
cat requirements.txt
echo "--- WEBHOOK SERVER (Head) ---"
head -n 30 webhook_server.py
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
