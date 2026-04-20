import hostinger_mcp
print(hostinger_mcp.ejecutar_comando_ssh('find /var/www /home -maxdepth 2 -iname "*remmi*"'))
