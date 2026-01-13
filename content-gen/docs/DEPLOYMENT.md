# Content Generation Solution Accelerator - Deployment Guide

This guide explains how to deploy and configure the Content Generation Solution Accelerator using Microsoft Agent Framework.

## Architecture Overview

The solution consists of:

- **Backend**: Python 3.11 + Quart + Hypercorn running in Azure Container Instance (ACI) with VNet integration
- **Frontend**: React + Vite + TypeScript + Fluent UI running on Azure App Service with Node.js proxy
- **AI Services**: 
  - Azure OpenAI (GPT model for text generation)
  - Azure OpenAI (DALL-E 3 for image generation - can be separate resource)
- **Data Services**:
  - Azure Cosmos DB (products catalog, conversations)
  - Azure Blob Storage (product images, generated images)
- **Networking**: 
  - Private VNet for backend container
  - App Service with VNet integration for frontend-to-backend communication
  - Private DNS zone for internal name resolution

## Prerequisites

1. **Azure Subscription** with sufficient quotas for:
   - Azure OpenAI (GPT-4 or GPT-5 model)
   - Azure OpenAI (DALL-E 3 model)
   - Azure Container Instance
   - Azure App Service (Basic tier or higher recommended)

2. **CLI Tools**:
   - Azure CLI (`az`) version 2.50 or later
   - Docker (optional - ACR can build containers)
   - Node.js 18+ (for frontend development)
   - Python 3.11+ (for local testing)

3. **Access Rights**:
   - Owner or Contributor on the resource group
   - Ability to create role assignments (User Access Administrator)

## Deployment Steps

### Step 1: Provision Azure Resources

If you haven't created the base infrastructure yet, create these resources:

```bash
# Set variables
RESOURCE_GROUP="rg-contentgen-yourname"
LOCATION="eastus"
ACR_NAME="acrcontentgenyourname"
STORAGE_NAME="storagecontentgenyourname"
COSMOS_NAME="cosmosdb-contentgen-yourname"
VNET_NAME="vnet-contentgen-yourname"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create VNet with subnets
az network vnet create \
    --resource-group $RESOURCE_GROUP \
    --name $VNET_NAME \
    --address-prefix 10.0.0.0/16

az network vnet subnet create \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --name subnet-aci \
    --address-prefix 10.0.4.0/24 \
    --delegations Microsoft.ContainerInstance/containerGroups

az network vnet subnet create \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --name subnet-appservice \
    --address-prefix 10.0.1.0/24 \
    --delegations Microsoft.Web/serverFarms

# Create Container Registry
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Create Storage Account
az storage account create \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_NAME \
    --sku Standard_LRS \
    --kind StorageV2

# Create blob containers
az storage container create \
    --account-name $STORAGE_NAME \
    --name product-images

az storage container create \
    --account-name $STORAGE_NAME \
    --name generated-images

# Create Cosmos DB
az cosmosdb create \
    --resource-group $RESOURCE_GROUP \
    --name $COSMOS_NAME \
    --kind GlobalDocumentDB \
    --default-consistency-level Session

az cosmosdb sql database create \
    --account-name $COSMOS_NAME \
    --resource-group $RESOURCE_GROUP \
    --name content-generation

az cosmosdb sql container create \
    --account-name $COSMOS_NAME \
    --resource-group $RESOURCE_GROUP \
    --database-name content-generation \
    --name products \
    --partition-key-path "/category"

az cosmosdb sql container create \
    --account-name $COSMOS_NAME \
    --resource-group $RESOURCE_GROUP \
    --database-name content-generation \
    --name conversations \
    --partition-key-path "/user_id"
```

### Step 2: Build and Deploy Backend Container

```bash
cd content-gen/src

# Login to ACR
az acr login --name $ACR_NAME

# Build using ACR tasks
az acr build \
    --registry $ACR_NAME \
    --image contentgen-backend:latest \
    --file WebApp.Dockerfile \
    .
```

### Step 3: Deploy Azure Container Instance

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Get VNet subnet ID
SUBNET_ID=$(az network vnet subnet show \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --name subnet-aci \
    --query "id" -o tsv)

# Create ACI with system-assigned managed identity
az container create \
    --resource-group $RESOURCE_GROUP \
    --name aci-contentgen-backend \
    --image "$ACR_NAME.azurecr.io/contentgen-backend:latest" \
    --registry-login-server "$ACR_NAME.azurecr.io" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --ip-address Private \
    --subnet "$SUBNET_ID" \
    --assign-identity \
    --environment-variables \
        AZURE_OPENAI_ENDPOINT="<your-gpt-endpoint>" \
        AZURE_OPENAI_DEPLOYMENT_NAME="<your-gpt-deployment>" \
        AZURE_OPENAI_DALLE_ENDPOINT="<your-dalle-endpoint>" \
        AZURE_OPENAI_DALLE_DEPLOYMENT="dall-e-3" \
        COSMOS_ENDPOINT="https://$COSMOS_NAME.documents.azure.com:443/" \
        COSMOS_DATABASE="content-generation" \
        AZURE_STORAGE_ACCOUNT_NAME="$STORAGE_NAME" \
        AZURE_STORAGE_CONTAINER="product-images" \
        AZURE_STORAGE_GENERATED_CONTAINER="generated-images"
```

### Step 4: Assign RBAC Roles

Run the RBAC assignment script:

```bash
./scripts/assign_rbac_roles.sh
```

Or manually assign roles:

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az container show -g $RESOURCE_GROUP -n aci-contentgen-backend --query "identity.principalId" -o tsv)

# Azure OpenAI - GPT
GPT_RESOURCE_ID=$(az cognitiveservices account show --name <gpt-resource> --resource-group <gpt-rg> --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "Cognitive Services OpenAI User" --scope $GPT_RESOURCE_ID

# Azure OpenAI - DALL-E (if separate resource)
DALLE_RESOURCE_ID=$(az cognitiveservices account show --name <dalle-resource> --resource-group <dalle-rg> --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "Cognitive Services OpenAI User" --scope $DALLE_RESOURCE_ID

# Cosmos DB - Data plane access
az cosmosdb sql role assignment create \
    --account-name $COSMOS_NAME \
    --resource-group $RESOURCE_GROUP \
    --scope "/" \
    --principal-id $PRINCIPAL_ID \
    --role-definition-id "00000000-0000-0000-0000-000000000002"

# Cosmos DB - Account metadata
COSMOS_RESOURCE_ID=$(az cosmosdb show --name $COSMOS_NAME --resource-group $RESOURCE_GROUP --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "Cosmos DB Account Reader Role" --scope $COSMOS_RESOURCE_ID

# Blob Storage
STORAGE_RESOURCE_ID=$(az storage account show --name $STORAGE_NAME --resource-group $RESOURCE_GROUP --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "Storage Blob Data Contributor" --scope $STORAGE_RESOURCE_ID
```

### Step 5: Create Private DNS Zone

```bash
# Create private DNS zone
az network private-dns zone create \
    --resource-group $RESOURCE_GROUP \
    --name contentgen.internal

# Link to VNet
az network private-dns link vnet create \
    --resource-group $RESOURCE_GROUP \
    --zone-name contentgen.internal \
    --name link-contentgen-vnet \
    --virtual-network $VNET_NAME \
    --registration-enabled false

# Get ACI IP address
ACI_IP=$(az container show -g $RESOURCE_GROUP -n aci-contentgen-backend --query "ipAddress.ip" -o tsv)

# Create A record for backend
az network private-dns record-set a add-record \
    --resource-group $RESOURCE_GROUP \
    --zone-name contentgen.internal \
    --record-set-name backend \
    --ipv4-address $ACI_IP
```

### Step 6: Deploy Frontend to App Service

```bash
# Create App Service Plan
az appservice plan create \
    --resource-group $RESOURCE_GROUP \
    --name asp-contentgen \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan asp-contentgen \
    --name app-contentgen-yourname \
    --runtime "NODE|18-lts"

# Enable VNet integration
az webapp vnet-integration add \
    --resource-group $RESOURCE_GROUP \
    --name app-contentgen-yourname \
    --vnet $VNET_NAME \
    --subnet subnet-appservice

# Configure app settings
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name app-contentgen-yourname \
    --settings \
        BACKEND_URL="http://backend.contentgen.internal:8000" \
        WEBSITES_PORT="3000" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Disable HTTP/2 for SSE streaming
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name app-contentgen-yourname \
    --http20-enabled false

# Build and deploy frontend
cd content-gen/src/app/frontend
npm install
npm run build

cd ../frontend-server
zip -r frontend-deploy.zip static/ server.js package.json package-lock.json

az webapp deploy \
    --resource-group $RESOURCE_GROUP \
    --name app-contentgen-yourname \
    --src-path frontend-deploy.zip \
    --type zip
```

## Troubleshooting

### 401 Unauthorized Errors

**Symptom**: API calls return 401 errors

**Cause**: Missing RBAC role assignments

**Solution**: Run `assign_rbac_roles.sh` and wait 5-10 minutes for propagation

### 403 Forbidden from Cosmos DB

**Symptom**: Cosmos DB operations fail with 403

**Cause**: Missing Cosmos DB data plane role (not ARM role)

**Solution**: Use `az cosmosdb sql role assignment create` (not `az role assignment create`)

### SSE Streaming Not Working

**Symptom**: Long responses timeout, no streaming updates

**Causes**:
1. HTTP/2 enabled on App Service (breaks SSE)
2. Proxy timeout too short

**Solution**:
```bash
# Disable HTTP/2
az webapp config set -g $RESOURCE_GROUP -n <app-name> --http20-enabled false

# Verify server.js has proxyTimeout: 300000
```

### Container Cannot Reach AI Services

**Symptom**: 401 from Azure OpenAI even with correct roles

**Cause**: AI resources may be in different resource groups

**Solution**: Ensure role assignments are on the correct resources:
- Check which resource group contains your GPT model
- Check which resource group contains your DALL-E model
- Assign roles to those specific resources

### Backend Not Accessible

**Symptom**: Frontend cannot reach backend API

**Cause**: VNet/DNS configuration issues

**Solution**:
1. Verify VNet integration is enabled on App Service
2. Verify private DNS zone is linked to VNet
3. Verify A record points to correct ACI IP
4. Check if ACI IP changed (run `update_backend_dns.sh`)

## Environment Variables Reference

### Backend (ACI)

| Variable | Description | Example |
|----------|-------------|---------|
| AZURE_OPENAI_ENDPOINT | GPT model endpoint | https://ai-account.cognitiveservices.azure.com/ |
| AZURE_OPENAI_DEPLOYMENT_NAME | GPT deployment name | gpt-5.1 |
| AZURE_OPENAI_DALLE_ENDPOINT | DALL-E endpoint | https://dalle-account.cognitiveservices.azure.com/ |
| AZURE_OPENAI_DALLE_DEPLOYMENT | DALL-E deployment name | dall-e-3 |
| COSMOS_ENDPOINT | Cosmos DB endpoint | https://cosmos.documents.azure.com:443/ |
| COSMOS_DATABASE | Database name | content-generation |
| AZURE_STORAGE_ACCOUNT_NAME | Storage account | storagecontentgen |
| AZURE_STORAGE_CONTAINER | Product images container | product-images |
| AZURE_STORAGE_GENERATED_CONTAINER | Generated images container | generated-images |

### Frontend (App Service)

| Variable | Description | Example |
|----------|-------------|---------|
| BACKEND_URL | Backend API URL | http://backend.contentgen.internal:8000 |
| WEBSITES_PORT | App Service port | 3000 |

## Updating the Deployment

### Update Backend Container

```bash
# Build new version
az acr build --registry $ACR_NAME --image contentgen-backend:v2 --file WebApp.Dockerfile .

# Update ACI (or restart to pull latest)
az container restart -g $RESOURCE_GROUP -n aci-contentgen-backend
```

### Update Frontend

```bash
cd content-gen/src/app/frontend
npm run build
cd ../frontend-server
zip -r frontend-deploy.zip static/ server.js package.json package-lock.json
az webapp deploy -g $RESOURCE_GROUP -n <app-name> --src-path frontend-deploy.zip --type zip
```

## Security Considerations

1. **Managed Identity**: The solution uses system-assigned managed identity instead of connection strings
2. **Private VNet**: Backend runs in private subnet, not exposed to internet
3. **RBAC**: Principle of least privilege - only necessary roles are assigned
4. **No Secrets in Code**: All credentials managed through Azure identity
