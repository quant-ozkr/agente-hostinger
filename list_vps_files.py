import sys
import os
# Add the scripts directory to sys.path so we can import hostinger_mcp
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "ls -R /var/www/tesis-app"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
