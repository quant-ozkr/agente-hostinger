import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# DATABASE WAS ALREADY CREATED in previous step
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE liq_mkt TO \\"rootAdminLiq\\";"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
