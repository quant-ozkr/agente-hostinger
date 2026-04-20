import os
import hostinger_mcp

pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDYt9Pg319k/3t7kCUk7gQFUntyNGPV8jhO0fPMDHVWIDiJOP4RqngYZnAWzNCfXyx164XF92TOIWoa3T9i9cluB3ObkvLvGCY8i3IoTTim+3gAOVBe5c5wNZmRqVW3qkQNv15eGQzNkOxtZmaiKqrFjM7scbMiyUAhVX3gUpT8RJJBRE4OL/jk44MF+sZejAjgnO2OdBrIWK4QU2szv4Qhdhze3al0QPbyptHomYqf1mBf6Z1y8EAq2k/5omMrOA/AnkyQZASAAWyZl+rM9DzzJ4H32k7Aek9nuEYAiDVzgZPLO4zozbued09TaC3hE2dJRIjrn8KNduhOFaanO1S/kXwSGPQ72y56qu3nIWmeCNccMU3IFR/dfhZsX7oWeHDTpmZSnmPv2QFTIMlob8wpy4l2Q5MdlL8iD6hR5JURouPND9tQv7GehOfcdpeKsLfYWfGP9CGfWfCI4l/PODE+GnHNnRUcPRyv2xJpeHwb26NmBvnz7zhMKMlLmfSPUqc+MxG21kdpm9wU15Bm30M+1hiHn0eG+Q7DG0uLFdLQl/kWrZQpoeKW/AGe8LD0OIGznvxvPOpEX4pQdP+pCN+Pfh5AqzP6j6I4Sb6Q18lAVHwBMtyzw4Sy3L/uueA3tXk6KfGCSHZDlPHI18vEGrAXUbWsNBBBaJpl3AmQJfFldw== oscar@Mentess"

# 1. Crear usuario tesis si no existe y dar permisos de sudo
# 2. Instalar la llave pública
cmd = f"""
if ! id -u tesis > /dev/null 2>&1; then
    adduser --disabled-password --gecos "" tesis
    usermod -aG sudo tesis
fi
mkdir -p /home/tesis/.ssh
echo "{pub_key}" > /home/tesis/.ssh/authorized_keys
chown -R tesis:tesis /home/tesis/.ssh
chmod 700 /home/tesis/.ssh
chmod 600 /home/tesis/.ssh/authorized_keys
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
