#!/bin/bash
# =============================================================================
# Local Development Script for Content Generation Accelerator
# =============================================================================
#
# This script sets up and runs the application locally for development.
#
# Usage:
#   ./local_dev.sh              # Start both backend and frontend
#   ./local_dev.sh backend      # Start only the backend
#   ./local_dev.sh frontend     # Start only the frontend
#   ./local_dev.sh setup        # Set up virtual environment and install dependencies
#   ./local_dev.sh env          # Generate .env file from Azure resources
#
# Prerequisites:
#   - Python 3.11+
#   - Node.js 18+
#   - Azure CLI (for fetching environment variables)
#   - Azure Developer CLI (azd) - optional, for env generation
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
FRONTEND_DIR="$SRC_DIR/frontend"

# Default ports
BACKEND_PORT=${BACKEND_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        return 1
    fi
    return 0
}

# =============================================================================
# Setup Function
# =============================================================================

setup() {
    print_header "Setting Up Local Development Environment"
    
    cd "$PROJECT_ROOT"
    
    # Check Python
    print_info "Checking Python installation..."
    if ! check_command python3; then
        exit 1
    fi
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $python_version found"
    
    # Check Node.js
    print_info "Checking Node.js installation..."
    if ! check_command node; then
        exit 1
    fi
    node_version=$(node --version)
    print_success "Node.js $node_version found"
    
    # Create virtual environment
    print_info "Creating Python virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install Python dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip > /dev/null
    pip install -r "$SRC_DIR/requirements.txt" > /dev/null 2>&1
    print_success "Python dependencies installed"
    
    # Install frontend dependencies
    print_info "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install > /dev/null 2>&1
    print_success "Frontend dependencies installed"
    
    cd "$PROJECT_ROOT"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f ".env.template" ]; then
            print_info "Copying .env.template to .env..."
            cp .env.template .env
            print_warning "Please update .env with your Azure resource values"
        fi
    else
        print_success ".env file found"
    fi
    
    print_header "Setup Complete!"
    echo -e "To start development, run: ${GREEN}./scripts/local_dev.sh${NC}"
    echo -e "Or start individually:"
    echo -e "  Backend:  ${GREEN}./scripts/local_dev.sh backend${NC}"
    echo -e "  Frontend: ${GREEN}./scripts/local_dev.sh frontend${NC}"
}

# =============================================================================
# Environment Generation Function
# =============================================================================

generate_env() {
    print_header "Generating Environment Variables from Azure"
    
    cd "$PROJECT_ROOT"
    
    # Check Azure CLI
    if ! check_command az; then
        print_error "Azure CLI is required for environment generation"
        exit 1
    fi
    
    # Check if logged in
    print_info "Checking Azure CLI login status..."
    if ! az account show &> /dev/null; then
        print_error "Not logged into Azure CLI. Please run: az login"
        exit 1
    fi
    
    account_name=$(az account show --query name -o tsv)
    print_success "Logged in as: $account_name"
    
    # If using azd
    if command -v azd &> /dev/null && [ -f "azure.yaml" ]; then
        print_info "Azure Developer CLI detected. Generating .env from azd..."
        azd env get-values > .env.azd 2>/dev/null || true
        
        if [ -s ".env.azd" ]; then
            print_success "Environment variables exported to .env.azd"
            print_info "Merging with .env..."
            
            # Merge with existing .env
            if [ -f ".env" ]; then
                # Backup existing
                cp .env .env.backup
                # Append new values (avoiding duplicates)
                while IFS= read -r line; do
                    key=$(echo "$line" | cut -d'=' -f1)
                    if ! grep -q "^$key=" .env 2>/dev/null; then
                        echo "$line" >> .env
                    fi
                done < .env.azd
            else
                mv .env.azd .env
            fi
            rm -f .env.azd
            print_success "Environment variables merged"
        fi
    else
        print_warning "Azure Developer CLI not found or no azure.yaml"
        print_info "Please manually update .env with your Azure resource values"
        
        if [ ! -f ".env" ] && [ -f ".env.template" ]; then
            cp .env.template .env
            print_info "Created .env from template"
        fi
    fi
    
    print_success "Environment setup complete"
    print_warning "Review .env and ensure all required values are set"
}

# =============================================================================
# Backend Start Function
# =============================================================================

start_backend() {
    print_header "Starting Backend Server"
    
    cd "$PROJECT_ROOT"
    
    # Check for .env
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    # Activate virtual environment
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    # Set environment variables
    export PYTHONPATH="$SRC_DIR"
    export DOTENV_PATH="$PROJECT_ROOT/.env"
    
    # Load .env file
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    
    print_info "Starting Quart backend on port $BACKEND_PORT..."
    print_info "API will be available at: http://localhost:$BACKEND_PORT"
    print_info "Health check: http://localhost:$BACKEND_PORT/api/health"
    echo ""
    
    cd "$SRC_DIR"
    
    # Use hypercorn for async support (same as production)
    if command -v hypercorn &> /dev/null; then
        hypercorn app:app --bind "0.0.0.0:$BACKEND_PORT" --reload
    else
        # Fallback to quart run
        python -m quart --app app:app run --host 0.0.0.0 --port "$BACKEND_PORT" --reload
    fi
}

# =============================================================================
# Frontend Start Function
# =============================================================================

start_frontend() {
    print_header "Starting Frontend Development Server"
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "Node modules not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    print_info "Starting Vite dev server on port $FRONTEND_PORT..."
    print_info "Frontend will be available at: http://localhost:$FRONTEND_PORT"
    print_info "API requests will proxy to: http://localhost:$BACKEND_PORT"
    echo ""
    
    npm run dev
}

# =============================================================================
# Start Both (using background processes)
# =============================================================================

start_all() {
    print_header "Starting Full Development Environment"
    
    cd "$PROJECT_ROOT"
    
    # Check prerequisites
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_error "Frontend dependencies not found. Run: ./scripts/local_dev.sh setup"
        exit 1
    fi
    
    print_info "Starting backend and frontend in parallel..."
    print_info ""
    print_info "Services:"
    print_info "  Backend API:  http://localhost:$BACKEND_PORT"
    print_info "  Frontend:     http://localhost:$FRONTEND_PORT"
    print_info ""
    print_info "Press Ctrl+C to stop all services"
    echo ""
    
    # Trap Ctrl+C to kill all background jobs
    trap 'echo ""; print_info "Stopping all services..."; kill $(jobs -p) 2>/dev/null; exit 0' INT TERM
    
    # Start backend in background
    (
        cd "$PROJECT_ROOT"
        source .venv/bin/activate
        export PYTHONPATH="$SRC_DIR"
        export DOTENV_PATH="$PROJECT_ROOT/.env"
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
        cd "$SRC_DIR"
        
        if command -v hypercorn &> /dev/null; then
            hypercorn app:app --bind "0.0.0.0:$BACKEND_PORT" --reload 2>&1 | sed 's/^/[Backend] /'
        else
            python -m quart --app app:app run --host 0.0.0.0 --port "$BACKEND_PORT" --reload 2>&1 | sed 's/^/[Backend] /'
        fi
    ) &
    
    # Give backend a moment to start
    sleep 2
    
    # Start frontend in background
    (
        cd "$FRONTEND_DIR"
        npm run dev 2>&1 | sed 's/^/[Frontend] /'
    ) &
    
    # Wait for all background jobs
    wait
}

# =============================================================================
# Build Function
# =============================================================================

build() {
    print_header "Building for Production"
    
    cd "$FRONTEND_DIR"
    
    print_info "Building frontend..."
    npm run build
    
    print_success "Build complete!"
    print_info "Static files are in: $SRC_DIR/static"
}

# =============================================================================
# Clean Function
# =============================================================================

clean() {
    print_header "Cleaning Development Environment"
    
    cd "$PROJECT_ROOT"
    
    print_info "Removing Python cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_info "Removing node_modules..."
    rm -rf "$FRONTEND_DIR/node_modules" 2>/dev/null || true
    
    print_info "Removing build artifacts..."
    rm -rf "$SRC_DIR/static" 2>/dev/null || true
    
    print_success "Clean complete!"
}

# =============================================================================
# Main Script
# =============================================================================

case "${1:-}" in
    setup)
        setup
        ;;
    env)
        generate_env
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    build)
        build
        ;;
    clean)
        clean
        ;;
    ""|all)
        start_all
        ;;
    *)
        echo "Content Generation Accelerator - Local Development"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     Set up virtual environment and install dependencies"
        echo "  env       Generate .env file from Azure resources"
        echo "  backend   Start only the backend server"
        echo "  frontend  Start only the frontend dev server"
        echo "  all       Start both backend and frontend (default)"
        echo "  build     Build frontend for production"
        echo "  clean     Remove cache and build artifacts"
        echo ""
        echo "Environment Variables:"
        echo "  BACKEND_PORT   Backend port (default: 5000)"
        echo "  FRONTEND_PORT  Frontend port (default: 3000)"
        ;;
esac
