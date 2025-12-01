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
echo "  - Azure AI Foundry (GPT-5.1 for text generation)"
echo "  - Azure OpenAI (DALL-E 3 for image generation - may require separate resource)"
echo "  - Azure Cosmos DB (products, conversations)"
echo "  - Azure Blob Storage (product-images, generated-images)"
echo "  - Azure AI Search (products index, product-images index)"
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
    
    # Upload product images and create search indexes
    read -p "Upload sample product images and create search indexes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Uploading product images to blob storage..."
        python scripts/upload_images.py
        echo ""
        echo "Creating product search index..."
        python scripts/index_products.py
        echo ""
        echo "Creating image search index with vector embeddings..."
        python scripts/create_image_search_index.py
        echo ""
        echo "Sample data and indexes created successfully!"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Visit the application URL to start using the Content Generation Accelerator"
    echo "2. Configure brand guidelines in the .env file or Azure App Configuration"
    echo "3. If DALL-E is in a separate resource, set AZURE_OPENAI_DALLE_ENDPOINT in .env"
    echo "4. Add your product catalog via the API or CosmosDB"
    echo "5. Ensure RBAC roles are assigned for Azure OpenAI access:"
    echo "   - Cognitive Services OpenAI User on GPT resource"
    echo "   - Cognitive Services OpenAI User on DALL-E resource (if separate)"
    echo ""
else
    echo "Deployment cancelled."
fi
