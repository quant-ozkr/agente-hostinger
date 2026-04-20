import hostinger_mcp
print(hostinger_mcp.ejecutar_comando_ssh('sudo -u postgres psql -d liqExpert -c "\dt"'))
