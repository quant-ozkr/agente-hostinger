import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# Generar clave RSA 4096 en formato PEM tradicional
ssh-keygen -t rsa -b 4096 -m PEM -f ~/.ssh/github_rsa_key -N "" -q -C "github-actions-rsa"
cat ~/.ssh/github_rsa_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "--- COPIA DESDE ESTA LÍNEA ---"
cat ~/.ssh/github_rsa_key
echo "--- HASTA ESTA LÍNEA ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
