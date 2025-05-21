#!/bin/bash

# Update Azure CLI
echo "Updating Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

git fetch
git pull

# provide execute permission to quotacheck script
sudo chmod +x ./scripts/quota_check_params.sh