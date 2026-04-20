import hostinger_mcp
cmd = 'echo "tesis ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/tesis && chmod 440 /etc/sudoers.d/tesis'
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
