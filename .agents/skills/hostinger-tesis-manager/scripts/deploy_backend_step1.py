import hostinger_mcp

repo_url = "https://github.com/quant-ozkr/tesis-calculadora-fiscal.git"

# 1. Crear directorios y clonar
# 2. Configurar venv
# 3. Instalar dependencias
cmd = f"""
sudo mkdir -p /var/www/tesis-app
sudo chown tesis:tesis /var/www/tesis-app
cd /var/www/tesis-app
if [ ! -d ".git" ]; then
    git clone {repo_url} .
fi
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --prefer-binary -r requirements.txt
pip install --prefer-binary -r requirements-rag.txt
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
