import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/agencia-mkt
grep -C 5 "DATABASE_URL" database/models.py
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
