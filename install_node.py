import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && \
sudo apt-get install -y nodejs
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
