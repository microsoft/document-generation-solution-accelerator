#!/bin/bash
# Script to assign RBAC roles for Content Generation Solution Accelerator
#
# This script assigns all required RBAC roles to the managed identity
# used by the Azure Container Instance backend.
#
# Required roles:
# - Cognitive Services OpenAI User (GPT resource)
# - Cognitive Services OpenAI User (DALL-E resource - may be separate)
# - Cosmos DB Built-in Data Contributor (data plane access)
# - Cosmos DB Account Reader Role (metadata access)
# - Storage Blob Data Contributor (blob storage)

set -e

echo "============================================"
echo "RBAC Role Assignment Script"
echo "Content Generation Solution Accelerator"
echo "============================================"
echo ""

# Configuration - set these or pass as environment variables
RESOURCE_GROUP="${RESOURCE_GROUP:-}"
CONTAINER_NAME="${CONTAINER_NAME:-aci-contentgen-backend}"

# Azure OpenAI resources
GPT_RESOURCE_NAME="${GPT_RESOURCE_NAME:-}"
GPT_RESOURCE_GROUP="${GPT_RESOURCE_GROUP:-}"  # May be different from main RG

DALLE_RESOURCE_NAME="${DALLE_RESOURCE_NAME:-}"
DALLE_RESOURCE_GROUP="${DALLE_RESOURCE_GROUP:-}"  # May be different from main RG

# Cosmos DB
COSMOS_ACCOUNT_NAME="${COSMOS_ACCOUNT_NAME:-}"

# Storage Account
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-}"

# Prompt for missing values
if [ -z "$RESOURCE_GROUP" ]; then
    read -p "Enter main Resource Group name: " RESOURCE_GROUP
fi

if [ -z "$GPT_RESOURCE_NAME" ]; then
    read -p "Enter Azure OpenAI resource name (for GPT model): " GPT_RESOURCE_NAME
fi

if [ -z "$GPT_RESOURCE_GROUP" ]; then
    read -p "Enter Resource Group for GPT resource (press Enter if same as main RG): " GPT_RESOURCE_GROUP
    GPT_RESOURCE_GROUP="${GPT_RESOURCE_GROUP:-$RESOURCE_GROUP}"
fi

if [ -z "$DALLE_RESOURCE_NAME" ]; then
    read -p "Enter Azure OpenAI resource name for DALL-E (press Enter if same as GPT): " DALLE_RESOURCE_NAME
    DALLE_RESOURCE_NAME="${DALLE_RESOURCE_NAME:-$GPT_RESOURCE_NAME}"
fi

if [ -z "$DALLE_RESOURCE_GROUP" ]; then
    if [ "$DALLE_RESOURCE_NAME" == "$GPT_RESOURCE_NAME" ]; then
        DALLE_RESOURCE_GROUP="$GPT_RESOURCE_GROUP"
    else
        read -p "Enter Resource Group for DALL-E resource: " DALLE_RESOURCE_GROUP
    fi
fi

if [ -z "$COSMOS_ACCOUNT_NAME" ]; then
    read -p "Enter Cosmos DB account name: " COSMOS_ACCOUNT_NAME
fi

if [ -z "$STORAGE_ACCOUNT_NAME" ]; then
    read -p "Enter Storage account name: " STORAGE_ACCOUNT_NAME
fi

echo ""
echo "Configuration:"
echo "  Main Resource Group: $RESOURCE_GROUP"
echo "  Container Name: $CONTAINER_NAME"
echo "  GPT Resource: $GPT_RESOURCE_NAME (in $GPT_RESOURCE_GROUP)"
echo "  DALL-E Resource: $DALLE_RESOURCE_NAME (in $DALLE_RESOURCE_GROUP)"
echo "  Cosmos DB Account: $COSMOS_ACCOUNT_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT_NAME"
echo ""

read -p "Continue with RBAC assignment? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Get the managed identity principal ID
echo ""
echo "Getting managed identity for container $CONTAINER_NAME..."
PRINCIPAL_ID=$(az container show -g "$RESOURCE_GROUP" -n "$CONTAINER_NAME" --query "identity.principalId" -o tsv)

if [ -z "$PRINCIPAL_ID" ]; then
    echo "Error: Could not get managed identity. Does the container have system-assigned identity enabled?"
    exit 1
fi

echo "Principal ID: $PRINCIPAL_ID"
echo ""

# Get resource IDs
echo "Getting resource IDs..."

GPT_RESOURCE_ID=$(az cognitiveservices account show \
    --name "$GPT_RESOURCE_NAME" \
    --resource-group "$GPT_RESOURCE_GROUP" \
    --query "id" -o tsv)
echo "GPT Resource ID: $GPT_RESOURCE_ID"

if [ "$DALLE_RESOURCE_NAME" != "$GPT_RESOURCE_NAME" ]; then
    DALLE_RESOURCE_ID=$(az cognitiveservices account show \
        --name "$DALLE_RESOURCE_NAME" \
        --resource-group "$DALLE_RESOURCE_GROUP" \
        --query "id" -o tsv)
    echo "DALL-E Resource ID: $DALLE_RESOURCE_ID"
else
    DALLE_RESOURCE_ID="$GPT_RESOURCE_ID"
    echo "DALL-E using same resource as GPT"
fi

COSMOS_RESOURCE_ID=$(az cosmosdb show \
    --name "$COSMOS_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "id" -o tsv)
echo "Cosmos DB Resource ID: $COSMOS_RESOURCE_ID"

STORAGE_RESOURCE_ID=$(az storage account show \
    --name "$STORAGE_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "id" -o tsv)
echo "Storage Resource ID: $STORAGE_RESOURCE_ID"

echo ""

# 1. Azure OpenAI - GPT
echo "1. Assigning Cognitive Services OpenAI User on GPT resource..."
az role assignment create \
    --assignee "$PRINCIPAL_ID" \
    --role "Cognitive Services OpenAI User" \
    --scope "$GPT_RESOURCE_ID" \
    2>/dev/null && echo "   ✓ Role assigned" || echo "   ⚠ Role may already exist"

# 2. Azure OpenAI - DALL-E (if different resource)
if [ "$DALLE_RESOURCE_ID" != "$GPT_RESOURCE_ID" ]; then
    echo "2. Assigning Cognitive Services OpenAI User on DALL-E resource..."
    az role assignment create \
        --assignee "$PRINCIPAL_ID" \
        --role "Cognitive Services OpenAI User" \
        --scope "$DALLE_RESOURCE_ID" \
        2>/dev/null && echo "   ✓ Role assigned" || echo "   ⚠ Role may already exist"
else
    echo "2. DALL-E uses same resource as GPT - skipping"
fi

# 3. Cosmos DB - Data plane (using built-in role)
echo "3. Assigning Cosmos DB Built-in Data Contributor..."
az cosmosdb sql role assignment create \
    --account-name "$COSMOS_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --scope "/" \
    --principal-id "$PRINCIPAL_ID" \
    --role-definition-id "00000000-0000-0000-0000-000000000002" \
    2>/dev/null && echo "   ✓ Role assigned" || echo "   ⚠ Role may already exist"

# 4. Cosmos DB - Account Reader (metadata)
echo "4. Assigning Cosmos DB Account Reader Role..."
az role assignment create \
    --assignee "$PRINCIPAL_ID" \
    --role "Cosmos DB Account Reader Role" \
    --scope "$COSMOS_RESOURCE_ID" \
    2>/dev/null && echo "   ✓ Role assigned" || echo "   ⚠ Role may already exist"

# 5. Storage - Blob Data Contributor
echo "5. Assigning Storage Blob Data Contributor..."
az role assignment create \
    --assignee "$PRINCIPAL_ID" \
    --role "Storage Blob Data Contributor" \
    --scope "$STORAGE_RESOURCE_ID" \
    2>/dev/null && echo "   ✓ Role assigned" || echo "   ⚠ Role may already exist"

echo ""
echo "============================================"
echo "RBAC role assignment complete!"
echo "============================================"
echo ""
echo "Note: Role assignments may take a few minutes to propagate."
echo "If you still see 401/403 errors, wait a few minutes and try again."
echo ""
