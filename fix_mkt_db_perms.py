import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo -u postgres psql -d liq_mkt -c "GRANT ALL ON SCHEMA public TO \\"rootAdminLiq\\";"
sudo -u postgres psql -d liq_mkt -c "ALTER SCHEMA public OWNER TO \\"rootAdminLiq\\";"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
