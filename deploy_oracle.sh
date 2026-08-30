#!/usr/bin/env bash
# ==============================================================================
# SecureBank Oracle Cloud Infrastructure (OCI) Automated Deployment Script
# Supports: Ubuntu 20.04 / 22.04 / 24.04 LTS & Oracle Linux on OCI Always Free
# ==============================================================================

set -e

echo "🚀 Starting Automated SecureBank Deployment on Oracle Cloud Infrastructure (OCI)..."

# 1. Open Ports in Oracle Cloud OS Firewall (iptables / ufw)
echo "🛡️ Configuring OCI OS firewall for Port 8000 & 80..."
if command -v iptables &> /dev/null; then
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save 2>/dev/null || true
    fi
fi

if command -v ufw &> /dev/null; then
    sudo ufw allow 8000/tcp 2>/dev/null || true
    sudo ufw allow 80/tcp 2>/dev/null || true
    sudo ufw allow 443/tcp 2>/dev/null || true
fi

# 2. Update System & Install Docker
if command -v apt-get &> /dev/null; then
    echo "📦 Updating Ubuntu packages and installing Docker..."
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release git
    
    if ! command -v docker &> /dev/null; then
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo usermod -aG docker "$USER"
    fi
elif command -v dnf &> /dev/null; then
    echo "📦 Updating Oracle Linux packages and installing Docker..."
    sudo dnf install -y dnf-utils git curl
    sudo dnf-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo 2>/dev/null || true
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER"
fi

# 3. Create Production .env
if [ ! -f .env ]; then
    echo "📄 Creating production .env file..."
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "oci_prod_secret_jwt_key_$(date +%s)")
    
    cat << EOF > .env
DATABASE_URL=postgresql+psycopg://securebank:securebank123@postgres:5432/securebank
REDIS_URL=redis://redis:6379

JWT_SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo "✅ Production .env created."
fi

# 4. Start Docker Containers
echo "🐳 Building and starting Docker containers..."
sudo docker compose up -d --build

# 5. Wait for Services
echo "⏳ Waiting 5 seconds for PostgreSQL and Redis to start..."
sleep 5

# 6. Run Database Migrations
echo "🗄️ Running Alembic database migrations..."
sudo docker compose exec -T api uv run alembic upgrade head

# 7. Health Check
echo "🔍 Verifying application health endpoint..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ SecureBank deployed successfully on Oracle Cloud!"
    OCI_IP=$(curl -s ifconfig.me 2>/dev/null || echo '<OCI_PUBLIC_IP>')
    echo "🌐 API is running live at http://${OCI_IP}:8000"
    echo "🔗 Swagger Docs: http://${OCI_IP}:8000/docs"
else
    echo "⚠️ Deployed, but health check failed. Check logs: sudo docker compose logs api"
fi
