#!/bin/bash
# Deployment script for Content Generation Solution Accelerator

set -e

echo "============================================"
echo "Content Generation Solution Accelerator"
echo "Deployment Script"
echo "============================================"

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v azd &> /dev/null; then
    echo "Error: Azure Developer CLI (azd) is not installed. Please install it first."
    exit 1
fi

# Check Azure login
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo "Not logged in to Azure. Running 'az login'..."
    az login
}

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if environment is initialized
if [ ! -f ".azure/config.json" ]; then
    echo "Initializing Azure Developer CLI environment..."
    azd init
fi

# Deploy infrastructure and application
echo ""
echo "Starting deployment..."
echo "This will deploy the following resources:"
echo "  - Azure AI Foundry (GPT-5, DALL-E 3)"
echo "  - Azure Cosmos DB (products, conversations)"
echo "  - Azure Blob Storage (images)"
echo "  - Azure AI Search"
echo "  - Azure App Service"
echo "  - Azure Key Vault"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Run azd up
    azd up
    
    echo ""
    echo "============================================"
    echo "Deployment complete!"
    echo "============================================"
    
    # Get deployment outputs
    echo ""
    echo "Getting deployment information..."
    
    # Show the app URL
    WEBAPP_URL=$(azd env get-values | grep WEBAPP_URL | cut -d'=' -f2 | tr -d '"')
    if [ -n "$WEBAPP_URL" ]; then
        echo ""
        echo "Application URL: $WEBAPP_URL"
        echo ""
    fi
    
    # Load sample data
    read -p "Load sample product data? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Loading sample data..."
        cd src
        python ../scripts/load_sample_data.py
        cd ..
        echo "Sample data loaded successfully!"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Visit the application URL to start using the Content Generation Accelerator"
    echo "2. Configure brand guidelines in the Azure Portal or .env file"
    echo "3. Add your product catalog via the API or CosmosDB"
    echo ""
else
    echo "Deployment cancelled."
fi
