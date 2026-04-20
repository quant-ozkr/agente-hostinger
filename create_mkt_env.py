import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cat <<'EOF' > /var/www/agencia-mkt/.env
# Database Configuration
DATABASE_URL=postgresql://rootAdminLiq:liqPassSecret*@localhost:5432/liq_mkt

# External APIs
SERPER_API_KEY=xxx
WHATSAPP_API_KEY=xxx
EMAIL_API_KEY=xxx

# LLM Configuration
LLM_MODEL=gemini/gemini-1.5-pro
GEMINI_API_KEY=xxx

# Channel Adapters
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ADMIN_CHAT_ID=xxx

# Security
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://liqexpert.com

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=xxx
SMTP_PASSWORD=xxx
EMAIL_FROM=noreply@liqexpert.com

# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=xxx
WHATSAPP_ACCESS_TOKEN=xxx
EOF
chmod 600 /var/www/agencia-mkt/.env
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
