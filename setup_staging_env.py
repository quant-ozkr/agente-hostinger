import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# Setup Backend
cd /var/www/tesis-staging/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --prefer-binary -r requirements.txt
pip install --prefer-binary -r requirements-rag.txt

# Create staging .env
cat <<EOF > .env
# Database
DATABASE_URL=postgresql://rootAdminLiq:liqPassSecret*@localhost:5432/liq_staging

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# URLs
FRONTEND_URL=https://staging.liqexpert.com
BACKEND_URL=https://staging.liqexpert.com

# APIs
LLM_PROVIDER=groq
GEMINI_API_KEY=xxx
GROQ_API_KEY=xxx
EOF
chmod 600 .env

# Initialize DB
export DATABASE_URL=postgresql://rootAdminLiq:liqPassSecret*@localhost:5432/liq_staging
python3 scripts/ensure_alembic.py
alembic upgrade head

# Setup Frontend
cd ../frontend
npm install
npm run build
mkdir -p ../backend/static
# Dist folder is inside frontend/ after build
cp -r dist/* ../backend/static/
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
