import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

# Repo URL using SSH
repo_ssh_url = "git@github.com:quant-ozkr/agencia-mkt-aut.git"

cmd = f"""
# Configurar SSH para usar la deploy key específica para MKT
cat <<EOF >> ~/.ssh/config

Host github-mkt
    HostName github.com
    IdentityFile ~/.ssh/mkt_agent_deploy_key
    StrictHostKeyChecking no
EOF
chmod 600 ~/.ssh/config

# Crear directorio para la agencia mkt
sudo mkdir -p /var/www/agencia-mkt
sudo chown tesis:tesis /var/www/agencia-mkt
cd /var/www/agencia-mkt

# Clonar usando el host alias definido arriba
if [ ! -d ".git" ]; then
    git clone git@github-mkt:quant-ozkr/agencia-mkt-aut.git .
else
    git pull origin main
fi

echo "--- REPO CLONED SUCCESSFULLY ---"
ls -F
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
