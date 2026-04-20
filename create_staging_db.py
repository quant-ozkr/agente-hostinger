import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo -u postgres psql -c "CREATE DATABASE liq_staging;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE liq_staging TO \\"rootAdminLiq\\";"
sudo -u postgres psql -d liq_staging -c "GRANT ALL ON SCHEMA public TO \\"rootAdminLiq\\";"
sudo -u postgres psql -d liq_staging -c "ALTER SCHEMA public OWNER TO \\"rootAdminLiq\\";"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
