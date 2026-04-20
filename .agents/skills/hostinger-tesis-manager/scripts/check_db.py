import hostinger_mcp
print(hostinger_mcp.ejecutar_comando_ssh('ss -nltp | grep 5432; sudo -u postgres psql -l'))
