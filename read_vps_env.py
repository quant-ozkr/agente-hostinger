import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "cat /var/www/tesis-app/backend/.env"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
