import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "ls -lh /var/www/tesis-app/backend/static"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
