import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo mkdir -p /var/www/tesis-staging
sudo chown tesis:tesis /var/www/tesis-staging
cd /var/www/tesis-staging

# Clonar usando el host alias 'github.com' que ya tiene la llave de la tesis
if [ ! -d ".git" ]; then
    git clone git@github.com:quant-ozkr/tesis-calculadora-fiscal.git .
    git checkout staging || git checkout -b staging
fi

echo "--- STAGING REPO CLONED ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
