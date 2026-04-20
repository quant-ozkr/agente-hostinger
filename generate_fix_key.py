import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

# Generamos una clave en formato PEM (el más compatible con GitHub Actions)
cmd = """
ssh-keygen -t ed25519 -m PEM -f ~/.ssh/github_vps_key -N "" -q -C "github-actions-liq"
cat ~/.ssh/github_vps_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "--- COPIA DESDE LA SIGUIENTE LÍNEA ---"
cat ~/.ssh/github_vps_key
echo "--- HASTA LA LÍNEA ANTERIOR ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
