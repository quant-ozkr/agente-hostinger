import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
export PGPASSWORD='liqPassSecret*'
psql -h localhost -U rootAdminLiq -d liq_mkt -f /tmp/mkt_data.sql
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
