import hostinger_mcp
cmd = 'ssh-keygen -t ed25519 -f ~/.ssh/github_deploy_key -N "" && cat ~/.ssh/github_deploy_key.pub'
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
