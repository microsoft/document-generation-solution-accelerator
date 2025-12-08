# Local Development Setup Guide

Follow the steps below to set up and run the **Document-Generation-Solution-Accelerator** locally.



## Prerequisites

Install these tools before you start:
- [Visual Studio Code](https://code.visualstudio.com/) with the following extensions:
  - [Azure Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)
  - [Bicep](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-bicep)
  - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python 3.11](https://www.python.org/downloads/). **Important:** Check "Add Python to PATH" during installation.
- [PowerShell 7.0+](https://github.com/PowerShell/PowerShell#get-powershell).
- [Node.js (LTS)](https://nodejs.org/en).
- [Git](https://git-scm.com/downloads).
- [Azure Developer CLI (azd) v1.18.0+](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd).
- [Microsoft ODBC Driver 17](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16) for SQL Server.


## Setup Steps

### Clone the Repository

Choose a location on your local machine where you want to store the project files. We recommend creating a dedicated folder for your development projects.

#### Using Command Line/Terminal

1. **Open your terminal or command prompt. Navigate to your desired directory and Clone the repository:**
   ```bash
   git clone https://github.com/microsoft/document-generation-solution-accelerator.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd document-generation-solution-accelerator
   ```

3. **Open the project in Visual Studio Code:**
   ```bash
   code .
   ```

## Local Setup/Deplpoyment

Follow these steps to set up and run the application locally:

## Local Deployment:

You can refer the local deployment guide here: [Local Deployment Guide](https://github.com/microsoft/document-generation-solution-accelerator/blob/main/docs/DeploymentGuide.md)

### 1. Open the App Folder
Navigate to the `src` directory of the repository using Visual Studio Code.

### 2. Configure Environment Variables
- Copy the `.env.sample` file to a new file named `.env`.
- Update the `.env` file with the required values from your Azure resource group in Azure Portal App Service environment variables.
- You can get all env value in your deployed resource group under App Service:
![Enviorment Variables](images/Enviorment_variables.png)
- Alternatively, if resources were
provisioned using `azd provision` or `azd up`, a `.env` file is automatically generated in the `.azure/<env-name>/.env`
file. To get your `<env-name>` run `azd env list` to see which env is default.

> **Note**: After adding all environment variables to the .env file, update the value of **'APP_ENV'** from:
```
APP_ENV="Prod"
```
**to:**
```
APP_ENV="Dev"
```

This change is required for running the application in local development mode.

### 3. Start the Application
- Run `start.cmd` (Windows) or `start.sh` (Linux/Mac) to:
  - Install backend dependencies.
  - Install frontend dependencies.
  - Build the frontend.
  - Start the backend server.
- Alternatively, you can run the backend in debug mode using the VS Code debug configuration defined in `.vscode/launch.json`.

## Running with Automated Script

For convenience, you can use the provided startup scripts that handle environment setup and start both services:

**Windows:**
```cmd
cd src
.\start.cmd
```

**macOS/Linux:**
```bash
cd src
chmod +x start.sh
./start.sh
```

## Running Backend and Frontend Separately

#### Step 1: Create Virtual Environment (Recommended)

Open your terminal and navigate to the root folder of the project, then create the virtual environment:

```bash
# Navigate to the project root folder
cd document-generation-solution-accelerator

# Create virtual environment in the root folder
python -m venv .venv

# Activate virtual environment (Windows)
.venv/Scripts/activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

> **Note**: After activation, you should see `(.venv)` in your terminal prompt indicating the virtual environment is active.

#### Step 2: Install Dependencies and Run

To develop and run the backend API locally:

```bash
# Navigate to the API folder (while virtual environment is activated)
cd src/

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install Fronend Packages
cd src/frontend
npm install
npm run build

# Run the backend API (Windows)
cd src/

start http://127.0.0.1:50505
call python -m uvicorn app:app --port 50505 --reload 

# Run the backend API (MacOs)
cd src/

open http://127.0.0.1:50505
python -m uvicorn app:app --port 50505 --reload

# Run the backend API (Linux)
cd src/

xdg-open http://127.0.0.1:50505
python -m uvicorn app:app --port 50505 --reload

```

> **Note**: Make sure your virtual environment is activated before running these commands. You should see `(.venv)` in your terminal prompt when the virtual environment is active.

The App will run on `http://127.0.0.1:50505/#/` by default.

## Troubleshooting

### Common Issues

#### Python Version Issues

```bash
# Check available Python versions
python3 --version
python3.12 --version

# If python3.12 not found, install it:
# Ubuntu: sudo apt install python3.12
# macOS: brew install python@3.12
# Windows: winget install Python.Python.3.12
```

#### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf .venv  # Linux/macOS
# or Remove-Item -Recurse .venv  # Windows PowerShell

uv venv .venv
# Activate and reinstall
source .venv/bin/activate  # Linux/macOS
# or .\.venv\Scripts\Activate.ps1  # Windows
uv sync --python 3.12
```

#### Permission Issues (Linux/macOS)

```bash
# Fix ownership of files
sudo chown -R $USER:$USER .

# Fix uv permissions
chmod +x ~/.local/bin/uv
```

#### Windows-Specific Issues

```powershell
# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Long path support (Windows 10 1607+, run as Administrator)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# SSL certificate issues
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org uv
```

### Azure Authentication Issues

```bash
# Login to Azure CLI
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Test authentication
az account show
```

### Environment Variable Issues

```bash
# Check environment variables are loaded
env | grep AZURE  # Linux/macOS
Get-ChildItem Env:AZURE*  # Windows PowerShell

# Validate .env file format
cat .env | grep -v '^#' | grep '='  # Should show key=value pairs
```

## Related Documentation

- [Deployment Guide](DeploymentGuide.md) - Instructions for production deployment.
- [Delete Resource Group](DeleteResourceGroup.md) - Steps to safely delete the Azure resource group created for the solution.
- [App Authentication Setup](AppAuthentication.md) - Guide to configure application authentication and add support for additional platforms.
- [Powershell Setup](PowershellSetup.md) - Instructions for setting up PowerShell and required scripts.
- [Quota Check](QuotaCheck.md) - Steps to verify Azure quotas and ensure required limits before deployment.