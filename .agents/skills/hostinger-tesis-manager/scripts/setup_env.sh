#!/bin/bash  
echo "⚙️ Configurando entorno para Agente VPS Tesis..."

if [ ! -d ".venv" ]; then  
    python3 -m venv .venv  
fi

source .venv/bin/activate  
pip install --upgrade pip  
pip install mcp paramiko python-dotenv

if [ ! -f ".env" ]; then  
    cat <<EOT > .env  
HOSTINGER_IP=tu_ip_del_vps  
HOSTINGER_PORT=2222  
HOSTINGER_USER=tesis  
SSH_KEY_PATH=/ruta/a/tu/.ssh/id_rsa  
EOT  
    echo "⚠️ Archivo .env creado. Por favor, configúralo."  
fi  
echo "🚀 Terminado."
