# PowerShell deployment script for Content Generation Solution Accelerator

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Content Generation Solution Accelerator" -ForegroundColor Cyan
Write-Host "Deployment Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$azCli = Get-Command az -ErrorAction SilentlyContinue
if (-not $azCli) {
    Write-Host "Error: Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

$azdCli = Get-Command azd -ErrorAction SilentlyContinue
if (-not $azdCli) {
    Write-Host "Error: Azure Developer CLI (azd) is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check Azure login
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
try {
    az account show | Out-Null
} catch {
    Write-Host "Not logged in to Azure. Running 'az login'..." -ForegroundColor Yellow
    az login
}

# Get current directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Set-Location $ProjectDir

# Check if environment is initialized
if (-not (Test-Path ".azure/config.json")) {
    Write-Host "Initializing Azure Developer CLI environment..." -ForegroundColor Yellow
    azd init
}

# Deploy infrastructure and application
Write-Host ""
Write-Host "Starting deployment..." -ForegroundColor Green
Write-Host "This will deploy the following resources:" -ForegroundColor White
Write-Host "  - Azure AI Foundry (GPT-5.1 for text generation)" -ForegroundColor White
Write-Host "  - Azure OpenAI (DALL-E 3 for image generation - may require separate resource)" -ForegroundColor White
Write-Host "  - Azure Cosmos DB (products, conversations)" -ForegroundColor White
Write-Host "  - Azure Blob Storage (product-images, generated-images)" -ForegroundColor White
Write-Host "  - Azure AI Search (products index, product-images index)" -ForegroundColor White
Write-Host "  - Azure App Service" -ForegroundColor White
Write-Host "  - Azure Key Vault" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Continue with deployment? (y/n)"

if ($continue -eq "y" -or $continue -eq "Y") {
    # Run azd up
    azd up
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "Deployment complete!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    
    # Get deployment outputs
    Write-Host ""
    Write-Host "Getting deployment information..." -ForegroundColor Yellow
    
    # Show the app URL
    $envValues = azd env get-values
    $webappUrl = ($envValues | Where-Object { $_ -match "WEBAPP_URL" }) -replace "WEBAPP_URL=", "" -replace '"', ""
    
    if ($webappUrl) {
        Write-Host ""
        Write-Host "Application URL: $webappUrl" -ForegroundColor Cyan
        Write-Host ""
    }
    
    # Upload product images and create search indexes
    $loadData = Read-Host "Upload sample product images and create search indexes? (y/n)"
    if ($loadData -eq "y" -or $loadData -eq "Y") {
        Write-Host "Uploading product images to blob storage..." -ForegroundColor Yellow
        python scripts/upload_images.py
        Write-Host ""
        Write-Host "Creating product search index..." -ForegroundColor Yellow
        python scripts/index_products.py
        Write-Host ""
        Write-Host "Creating image search index with vector embeddings..." -ForegroundColor Yellow
        python scripts/create_image_search_index.py
        Write-Host ""
        Write-Host "Sample data and indexes created successfully!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Visit the application URL to start using the Content Generation Accelerator" -ForegroundColor White
    Write-Host "2. Configure brand guidelines in the .env file or Azure App Configuration" -ForegroundColor White
    Write-Host "3. If DALL-E is in a separate resource, set AZURE_OPENAI_DALLE_ENDPOINT in .env" -ForegroundColor White
    Write-Host "4. Add your product catalog via the API or CosmosDB" -ForegroundColor White
    Write-Host "5. Ensure RBAC roles are assigned for Azure OpenAI access:" -ForegroundColor White
    Write-Host "   - Cognitive Services OpenAI User on GPT resource" -ForegroundColor White
    Write-Host "   - Cognitive Services OpenAI User on DALL-E resource (if separate)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
}
