import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

# Read the exported SQL file locally
with open('mkt_export.sql', 'r', encoding='utf-16') as f:
    sql_content = f.read()

# Escape single quotes for the bash command
sql_content_escaped = sql_content.replace("'", "'\\''")

# Write the content to the VPS
cmd = f"""
cat <<'EOF_SQL' > /tmp/mkt_data.sql
{sql_content}
EOF_SQL
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
