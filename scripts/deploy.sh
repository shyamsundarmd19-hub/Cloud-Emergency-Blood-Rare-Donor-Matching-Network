#!/usr/bin/env bash
# ==============================================================================
# LifeLine Native Deployment Script (EC2 Direct Hosting - No Docker)
# Location: scripts/deploy.sh
# Purpose: Pulls latest git commits, updates Python virtualenv, compiles React
#          SPA directly to /var/www/lifeline, and restarts systemd service.
# ==============================================================================

set -euo pipefail

# ANSI Color Codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Paths definition
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
VENV_DIR="${BACKEND_DIR}/venv"
WEB_ROOT="/var/www/lifeline"
BRANCH="${1:-main}"

log_info "Starting LifeLine native deployment from directory: ${ROOT_DIR}"
log_info "Target Git Branch: ${BRANCH}"

# 1. Update Git Repository
log_info "Pulling latest code from branch '${BRANCH}'..."
cd "${ROOT_DIR}"
git fetch origin "${BRANCH}"
git reset --hard "origin/${BRANCH}" || git pull origin "${BRANCH}"
log_success "Git workspace synchronized."

# 2. Update Python Virtual Environment & Dependencies
log_info "Updating backend virtual environment..."
if [ ! -d "${VENV_DIR}" ]; then
    log_warn "Virtualenv not found at ${VENV_DIR}. Creating new venv..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel --quiet
pip install -r "${BACKEND_DIR}/requirements.txt" --quiet
log_success "Backend dependencies installed successfully."

# 3. Database Migrations / Schema Initialization
if [ -f "${BACKEND_DIR}/alembic.ini" ]; then
    log_info "Executing Alembic database migrations..."
    cd "${BACKEND_DIR}"
    alembic upgrade head || log_warn "Alembic migration skipped or up to date."
fi

# 4. Compile React SPA to /var/www/lifeline
log_info "Building frontend React SPA production bundle..."
cd "${FRONTEND_DIR}"

if command -v npm &>/dev/null; then
    npm ci --silent || npm install --silent
    npm run build

    log_info "Deploying compiled assets to ${WEB_ROOT}..."
    sudo mkdir -p "${WEB_ROOT}"
    sudo rm -rf "${WEB_ROOT:?}"/*
    
    if [ -d "${FRONTEND_DIR}/dist" ]; then
        sudo cp -r "${FRONTEND_DIR}/dist"/* "${WEB_ROOT}/"
    elif [ -d "${FRONTEND_DIR}/build" ]; then
        sudo cp -r "${FRONTEND_DIR}/build"/* "${WEB_ROOT}/"
    else
        log_error "Frontend build directory (dist/ or build/) not found!"
    fi

    # Set web server permissions
    sudo chown -R www-data:www-data "${WEB_ROOT}" || sudo chown -R nginx:nginx "${WEB_ROOT}" || true
    sudo chmod -R 755 "${WEB_ROOT}"
    log_success "Frontend production bundle deployed to ${WEB_ROOT}."
else
    log_warn "Node/npm not detected. Skipping frontend build step."
fi

# 5. Restart LifeLine Systemd Service & Reload Nginx
log_info "Restarting LifeLine FastAPI systemd service..."
sudo systemctl daemon-reload
sudo systemctl restart lifeline.service
sudo systemctl reload nginx

# 6. Post-Deployment Verification Health Check
log_info "Performing live health check..."
sleep 2

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/health || echo "FAILED")
if [ "$HTTP_STATUS" == "200" ]; then
    log_success "Health check passed (HTTP 200 OK)."
else
    log_error "Health check failed with status: ${HTTP_STATUS}. Check 'journalctl -u lifeline -n 50 --no-pager'."
fi

log_success "=========================================================="
log_success "LifeLine Deployment Completed Successfully!"
log_success "Service Status: $(systemctl is-active lifeline.service)"
log_success "Nginx Status:   $(systemctl is-active nginx.service)"
log_success "=========================================================="
