import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

# We'll use a specific name for this deploy key to avoid confusion
cmd = """
ssh-keygen -t ed25519 -f ~/.ssh/mkt_agent_deploy_key -N "" -q
echo "--- PUBLIC KEY FOR GITHUB (Copy this to Repository Settings -> Deploy Keys) ---"
cat ~/.ssh/mkt_agent_deploy_key.pub
echo "--- END PUBLIC KEY ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
