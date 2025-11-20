#!/usr/bin/env pwsh

# Build and push Docker image to Azure Container Registry
# This script runs before azd provision to ensure the image exists before Container App creation

Write-Host "Starting Docker build and push to ACR..." -ForegroundColor Cyan

# Get environment variables
$registryName = $env:AZURE_CONTAINER_REGISTRY_NAME
$resourceGroup = $env:AZURE_RESOURCE_GROUP
$imageTag = if ($env:AZURE_CONTAINER_IMAGE_TAG) { $env:AZURE_CONTAINER_IMAGE_TAG } else { "latest_waf" }

if (-not $registryName) {
    # Try to get from .env file
    $registryName = $env:AZURE_CONTAINER_REGISTRY_ENDPOINT
    if ($registryName) {
        $registryName = $registryName -replace '\.azurecr\.io.*$', ''
    }
}

if (-not $registryName) {
    Write-Host "ERROR: AZURE_CONTAINER_REGISTRY_NAME not found. ACR must be provisioned first." -ForegroundColor Red
    Write-Host "Run 'azd provision' first to create the ACR, then run 'azd deploy'." -ForegroundColor Yellow
    exit 1
}

# Login to ACR
Write-Host "Logging in to ACR: $registryName..." -ForegroundColor Yellow
az acr login --name $registryName
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to login to ACR" -ForegroundColor Red
    exit 1
}

# Build Docker image
$imageName = "document-generation/backend"
$fullImageName = "${registryName}.azurecr.io/${imageName}:${imageTag}"

Write-Host "Building Docker image: $fullImageName" -ForegroundColor Yellow
docker build -f src/WebApp.Dockerfile -t $fullImageName --platform linux/amd64 ./src
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker build failed" -ForegroundColor Red
    exit 1
}

# Push to ACR
Write-Host "Pushing image to ACR..." -ForegroundColor Yellow
docker push $fullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker push failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Successfully built and pushed: $fullImageName" -ForegroundColor Green
