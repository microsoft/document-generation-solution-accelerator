#!/bin/bash

# Build and push Docker image to Azure Container Registry
# This script runs before azd provision to ensure the image exists before Container App creation

echo "Starting Docker build and push to ACR..."

# Get environment variables
REGISTRY_NAME="${AZURE_CONTAINER_REGISTRY_NAME}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP}"
IMAGE_TAG="${AZURE_CONTAINER_IMAGE_TAG:-latest_waf}"

if [ -z "$REGISTRY_NAME" ]; then
    # Try to get from AZURE_CONTAINER_REGISTRY_ENDPOINT
    if [ -n "$AZURE_CONTAINER_REGISTRY_ENDPOINT" ]; then
        REGISTRY_NAME=$(echo "$AZURE_CONTAINER_REGISTRY_ENDPOINT" | sed 's/\.azurecr\.io.*$//')
    fi
fi

if [ -z "$REGISTRY_NAME" ]; then
    echo "ERROR: AZURE_CONTAINER_REGISTRY_NAME not found. ACR must be provisioned first."
    echo "Run 'azd provision' first to create the ACR, then run 'azd deploy'."
    exit 1
fi

# Login to ACR
echo "Logging in to ACR: $REGISTRY_NAME..."
az acr login --name "$REGISTRY_NAME"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to login to ACR"
    exit 1
fi

# Build Docker image
IMAGE_NAME="document-generation/backend"
FULL_IMAGE_NAME="${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building Docker image: $FULL_IMAGE_NAME"
docker build -f src/WebApp.Dockerfile -t "$FULL_IMAGE_NAME" --platform linux/amd64 ./src
if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed"
    exit 1
fi

# Push to ACR
echo "Pushing image to ACR..."
docker push "$FULL_IMAGE_NAME"
if [ $? -ne 0 ]; then
    echo "ERROR: Docker push failed"
    exit 1
fi

echo "✓ Successfully built and pushed: $FULL_IMAGE_NAME"
