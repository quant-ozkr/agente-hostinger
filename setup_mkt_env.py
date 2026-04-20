import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/agencia-mkt
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
