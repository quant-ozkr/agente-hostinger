import hostinger_mcp

repo_ssh_url = "git@github.com:quant-ozkr/tesis-calculadora-fiscal.git"

# 1. Configurar SSH para usar la deploy key específica para GitHub
# 2. Clonar el repo
# 3. Configurar venv e instalar dependencias
cmd = f"""
mkdir -p ~/.ssh
cat <<EOF > ~/.ssh/config
Host github.com
    IdentityFile ~/.ssh/github_deploy_key
    StrictHostKeyChecking no
EOF
chmod 600 ~/.ssh/config

sudo mkdir -p /var/www/tesis-app
sudo chown tesis:tesis /var/www/tesis-app
cd /var/www/tesis-app

if [ ! -d ".git" ]; then
    git clone {repo_ssh_url} .
fi

if [ -d "backend" ]; then
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install --prefer-binary -r requirements.txt
    pip install --prefer-binary -r requirements-rag.txt
else
    echo "Error: No se encontró la carpeta 'backend' en el repositorio."
    ls -R
fi
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
