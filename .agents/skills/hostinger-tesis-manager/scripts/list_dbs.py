import hostinger_mcp
print(hostinger_mcp.ejecutar_comando_ssh('sudo -n -u postgres psql -lqt'))
