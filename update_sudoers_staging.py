import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo tee /etc/sudoers.d/tesis-deploy << 'EOF'
tesis ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart tesis-backend, /usr/bin/systemctl restart liq-mkt, /usr/bin/systemctl restart tesis-staging
EOF
sudo chmod 440 /etc/sudoers.d/tesis-deploy
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
