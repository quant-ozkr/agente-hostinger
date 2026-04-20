import hostinger_mcp

# 1. Configurar venv e instalar dependencias
# 2. Crear archivo .env para la app
cmd = """
cd /var/www/tesis-app/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --prefer-binary -r requirements.txt
pip install --prefer-binary -r requirements-rag.txt

# Crear el .env de la app
cat <<EOF > .env
# Database
DATABASE_URL=postgresql://rootAdminLiq:liqPassSecret*@localhost:5432/liqExpert

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8001

# APIs
LLM_PROVIDER=groq
GEMINI_API_KEY=xxx
GROQ_API_KEY=xxx
EOF
chmod 600 .env
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
