#!/usr/bin/env bash
# ==============================================================================
# LifeLine EC2 Automated Setup Script (Ubuntu 22.04 / 24.04 LTS)
# Configures: Nginx, Python 3 venv, PostgreSQL client libs, Swap file, Systemd
# Optimized for AWS Free Tier (t2.micro / t3.micro)
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Ensure script is run with sudo or as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run this script with sudo: sudo bash scripts/setup_ec2.sh"
fi

PROJECT_USER="ubuntu"
if ! id "$PROJECT_USER" &>/dev/null; then
    # Fallback to current sudo caller if not on standard Ubuntu AMI
    PROJECT_USER="${SUDO_USER:-$USER}"
fi

APP_DIR="/home/${PROJECT_USER}/lifeline"
BACKEND_DIR="${APP_DIR}/backend"
VENV_DIR="${BACKEND_DIR}/venv"
WEB_ROOT="/var/www/lifeline"

log_info "Target deployment user: ${PROJECT_USER}"
log_info "Target project directory: ${APP_DIR}"

# ------------------------------------------------------------------------------
# 1. AWS Free Tier Optimization: Setup 2GB Swap Space (Prevents OOM during pip/build)
# ------------------------------------------------------------------------------
if ! swapon --show | grep -q '/swapfile'; then
    log_info "Configuring 2GB Swap File for AWS Free Tier EC2..."
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    log_success "Swap file configured successfully."
else
    log_info "Swap space already active."
fi

# ------------------------------------------------------------------------------
# 2. System Packages Update & Installation
# ------------------------------------------------------------------------------
log_info "Updating system packages and installing dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    gcc \
    git \
    curl \
    ufw \
    ca-certificates

log_success "System packages installed."

# ------------------------------------------------------------------------------
# 3. Create Web Directory and Permissions
# ------------------------------------------------------------------------------
log_info "Setting up web directories at ${WEB_ROOT}..."
mkdir -p "${WEB_ROOT}"
chown -R "${PROJECT_USER}:${PROJECT_USER}" "${WEB_ROOT}"
chmod -R 755 "${WEB_ROOT}"

# Create a temporary fallback index.html if frontend is not yet built
if [ ! -f "${WEB_ROOT}/index.html" ]; then
    cat <<'EOF' > "${WEB_ROOT}/index.html"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LifeLine - Emergency Blood & Rare Donor Network</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #fffaf0; color: #7c2d12; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 10px 25px -5px rgba(249, 115, 22, 0.15); max-width: 520px; text-align: center; border: 1px solid #fed7aa; }
        h1 { color: #ea580c; margin-top: 0; }
        .status { display: inline-block; padding: 0.35rem 0.8rem; background: #ffedd5; color: #c2410c; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="card">
        <div class="status">● EC2 Web Server Active</div>
        <h1>LifeLine Cloud Node</h1>
        <p>The Nginx proxy and FastAPI services are operational. Build and upload your React frontend build to <code>/var/www/lifeline</code> to view the interface.</p>
        <p style="font-size: 0.875rem; color: #9a3412;">API Documentation is available at <a href="/docs" style="color: #ea580c; font-weight: bold;">/docs</a></p>
    </div>
</body>
</html>
EOF
    chown "${PROJECT_USER}:${PROJECT_USER}" "${WEB_ROOT}/index.html"
fi

# ------------------------------------------------------------------------------
# 4. Setup Python Virtual Environment & Install Dependencies
# ------------------------------------------------------------------------------
log_info "Configuring Python virtual environment at ${VENV_DIR}..."
mkdir -p "${BACKEND_DIR}"
sudo -u "${PROJECT_USER}" python3 -m venv "${VENV_DIR}"

if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
    log_info "Installing Python dependencies inside venv..."
    sudo -u "${PROJECT_USER}" "${VENV_DIR}/bin/pip install" --upgrade pip setuptools wheel
    sudo -u "${PROJECT_USER}" "${VENV_DIR}/bin/pip install" -r "${BACKEND_DIR}/requirements.txt"
    log_success "Python dependencies installed."
else
    log_warning "requirements.txt not found at ${BACKEND_DIR}/requirements.txt. Please install dependencies after cloning."
fi

# ------------------------------------------------------------------------------
# 5. Configure Systemd Service for LifeLine FastAPI Backend
# ------------------------------------------------------------------------------
log_info "Deploying systemd service..."
if [ -f "${APP_DIR}/scripts/lifeline.service" ]; then
    cp "${APP_DIR}/scripts/lifeline.service" /etc/systemd/system/lifeline.service
    # Update username dynamically if not default ubuntu
    if [ "$PROJECT_USER" != "ubuntu" ]; then
        sed -i "s|/home/ubuntu|/home/${PROJECT_USER}|g" /etc/systemd/system/lifeline.service
        sed -i "s|User=ubuntu|User=${PROJECT_USER}|g" /etc/systemd/system/lifeline.service
        sed -i "s|Group=ubuntu|Group=${PROJECT_USER}|g" /etc/systemd/system/lifeline.service
    fi
else
    log_warning "scripts/lifeline.service not found; creating systemd unit file inline..."
    cat <<EOF > /etc/systemd/system/lifeline.service
[Unit]
Description=LifeLine FastAPI Application Service
After=network.target

[Service]
Type=simple
User=${PROJECT_USER}
Group=${PROJECT_USER}
WorkingDirectory=${BACKEND_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=-${BACKEND_DIR}/.env
ExecStart=${VENV_DIR}/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lifeline-backend

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
systemctl enable lifeline.service
# Start or restart backend service if app.main exists
if [ -f "${BACKEND_DIR}/app/main.py" ]; then
    systemctl restart lifeline.service || log_warning "Failed to start lifeline.service. Check journalctl -u lifeline.service."
fi
log_success "Systemd service configured and enabled."

# ------------------------------------------------------------------------------
# 6. Configure Nginx Reverse Proxy
# ------------------------------------------------------------------------------
log_info "Configuring Nginx..."
if [ -f "${APP_DIR}/scripts/nginx.conf" ]; then
    cp "${APP_DIR}/scripts/nginx.conf" /etc/nginx/sites-available/lifeline
else
    log_error "scripts/nginx.conf not found. Ensure repository is placed at ${APP_DIR}."
fi

# Enable site and remove default
ln -sf /etc/nginx/sites-available/lifeline /etc/nginx/sites-enabled/lifeline
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
fi

nginx -t || log_error "Nginx configuration test failed."
systemctl restart nginx
log_success "Nginx successfully configured and reloaded."

# ------------------------------------------------------------------------------
# 7. Basic Firewall (UFW) Configuration
# ------------------------------------------------------------------------------
log_info "Configuring firewall rules for HTTP, HTTPS, and SSH..."
ufw allow 22/tcp || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
# Ensure port 8000 is internal only (not exposed externally)
ufw deny 8000/tcp || true

log_success "================================================================"
log_success "LifeLine Cloud Node Setup Complete!"
log_success "FastAPI Service:   systemctl status lifeline"
log_success "FastAPI Logs:      journalctl -u lifeline -f"
log_success "Nginx Service:     systemctl status nginx"
log_success "React Web Root:    ${WEB_ROOT}"
log_success "================================================================"
