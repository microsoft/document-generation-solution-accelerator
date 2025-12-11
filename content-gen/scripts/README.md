# Scripts

This folder contains utility scripts for deploying, managing, and developing the Content Generation Solution Accelerator.

## Local Development

The `local_dev` scripts provide a streamlined way to run the application locally for development.

### Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend build tools
- **Azure CLI** - For authentication and environment setup
- **Azure Developer CLI (azd)** - Optional, for automatic environment configuration

### Quick Start

**Linux/Mac:**
```bash
# First time setup
./scripts/local_dev.sh setup

# Start development servers
./scripts/local_dev.sh
```

**Windows PowerShell:**
```powershell
# First time setup
.\scripts\local_dev.ps1 -Command setup

# Start development servers
.\scripts\local_dev.ps1
```

### Commands

| Command | Description |
|---------|-------------|
| `setup` | Create virtual environment, install Python and Node.js dependencies |
| `env` | Generate `.env` file from Azure resources (uses azd if available) |
| `backend` | Start only the Python/Quart backend server (port 5000) |
| `frontend` | Start only the Vite frontend dev server (port 3000) |
| `all` | Start both backend and frontend in parallel (default) |
| `build` | Build frontend for production |
| `clean` | Remove cache files, node_modules, and build artifacts |

### Usage Examples

**Linux/Mac:**
```bash
# Full setup and start
./scripts/local_dev.sh setup
./scripts/local_dev.sh

# Start only backend (for API development)
./scripts/local_dev.sh backend

# Start only frontend (if backend is running elsewhere)
./scripts/local_dev.sh frontend

# Generate environment from Azure
./scripts/local_dev.sh env

# Build for production
./scripts/local_dev.sh build

# Clean up
./scripts/local_dev.sh clean
```

**Windows PowerShell:**
```powershell
# Full setup and start
.\scripts\local_dev.ps1 -Command setup
.\scripts\local_dev.ps1

# Start only backend
.\scripts\local_dev.ps1 -Command backend

# Start only frontend
.\scripts\local_dev.ps1 -Command frontend

# Generate environment from Azure
.\scripts\local_dev.ps1 -Command env
```

### Environment Variables

You can customize the ports using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | 5000 | Port for the Python backend API |
| `FRONTEND_PORT` | 3000 | Port for the Vite dev server |

Example:
```bash
BACKEND_PORT=8000 FRONTEND_PORT=3001 ./scripts/local_dev.sh
```

### Configuration

The scripts use a `.env` file in the `content-gen` directory for configuration. 

1. Copy the template:
   ```bash
   cp .env.template .env
   ```

2. Fill in your Azure resource values, or run:
   ```bash
   ./scripts/local_dev.sh env
   ```

Key environment variables:
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint
- `AZURE_OPENAI_GPT_MODEL` - GPT model deployment name
- `AZURE_OPENAI_IMAGE_MODEL` - Image generation model (dall-e-3 or gpt-image-1)
- `AZURE_COSMOS_ENDPOINT` - Cosmos DB endpoint
- `AZURE_BLOB_ACCOUNT_NAME` - Storage account name

### Development URLs

When running locally:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:5000 |
| Health Check | http://localhost:5000/api/health |

The frontend Vite dev server automatically proxies `/api/*` requests to the backend.

### Hot Reload

Both servers support hot reload:
- **Backend**: Uses Hypercorn with `--reload` flag
- **Frontend**: Uses Vite's built-in HMR (Hot Module Replacement)

Changes to source files will automatically trigger a reload.

---

## Deployment Scripts

### deploy.sh / deploy.ps1

Deployment scripts for Azure infrastructure and application code. See the main [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for details.

### assign_rbac_roles.sh

Assigns required RBAC roles to managed identities for Azure resources.

```bash
./scripts/assign_rbac_roles.sh \
  --subscription <subscription-id> \
  --resource-group <resource-group> \
  --identity-name <managed-identity-name>
```

---

## Data Scripts

### load_sample_data.py

Loads sample product data into Cosmos DB and uploads product images to Blob Storage.

```bash
python scripts/load_sample_data.py
```

### index_products.py

Creates and populates the Azure AI Search index with product data.

```bash
python scripts/index_products.py
```

### upload_images.py

Uploads images from a local directory to Azure Blob Storage.

```bash
python scripts/upload_images.py --source ./images --container product-images
```

### create_image_search_index.py

Creates an image search index in Azure AI Search for visual similarity search.

```bash
python scripts/create_image_search_index.py
```

---

## Testing Scripts

### test_content_generation.py

End-to-end test for the content generation pipeline.

```bash
python scripts/test_content_generation.py
```

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find and kill the process
lsof -i :5000
kill -9 <PID>
```

**Virtual environment issues:**
```bash
# Remove and recreate
rm -rf .venv
./scripts/local_dev.sh setup
```

**Node modules issues:**
```bash
# Clean and reinstall
./scripts/local_dev.sh clean
./scripts/local_dev.sh setup
```

**Azure authentication:**
```bash
# Re-authenticate
az login
az account set --subscription <subscription-id>
```
