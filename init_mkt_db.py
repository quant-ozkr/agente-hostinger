import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/agencia-mkt
source venv/bin/activate
python3 -c "from database.models import init_db; init_db()"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
