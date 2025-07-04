#!/bin/bash

# Variables
storageAccount="$1"
fileSystem="$2"
keyvaultName="$3"
cosmosDbAccountName="$4"
resourceGroupName="$5"
aiFoundryName="$6"
aiSearchName="$7"
managedIdentityClientId="$8"

# get parameters from azd env, if not provided
if [ -z "$resourceGroupName" ]; then
    resourceGroupName=$(azd env get-value RESOURCE_GROUP_NAME)
fi

if [ -z "$cosmosDbAccountName" ]; then
    cosmosDbAccountName=$(azd env get-value COSMOSDB_ACCOUNT_NAME)
fi

if [ -z "$storageAccount" ]; then
    storageAccount=$(azd env get-value STORAGE_ACCOUNT_NAME)
fi

if [ -z "$fileSystem" ]; then
    fileSystem=$(azd env get-value STORAGE_CONTAINER_NAME)
fi

if [ -z "$keyvaultName" ]; then
    keyvaultName=$(azd env get-value KEY_VAULT_NAME)
fi

if [ -z "$aiFoundryName" ]; then
    aiFoundryName=$(azd env get-value AI_FOUNDRY_NAME)
fi

if [ -z "$aiSearchName" ]; then
    aiSearchName=$(azd env get-value AI_SEARCH_SERVICE_NAME)
fi

azSubscriptionId=$(azd env get-value AZURE_SUBSCRIPTION_ID)

# Check if all required arguments are provided
if [ -z "$storageAccount" ] || [ -z "$fileSystem" ] || [ -z "$keyvaultName" ] || [ -z "$cosmosDbAccountName" ] || [ -z "$resourceGroupName" ] || [ -z "$aiFoundryName" ] || [ -z "$aiSearchName" ]; then
    echo "Usage: $0 <storageAccount> <storageContainerName> <keyvaultName> <cosmosDbAccountName> <resourceGroupName> <aiFoundryName> <aiSearchName>"
    exit 1
fi

# Authenticate with Azure
if az account show &> /dev/null; then
    echo "Already authenticated with Azure."
else
    if [ -n "$managedIdentityClientId" ]; then
        # Use managed identity if running in Azure
        echo "Authenticating with Managed Identity..."
        az login --identity --client-id ${managedIdentityClientId}
    else
        # Use Azure CLI login if running locally
        echo "Authenticating with Azure CLI..."
        az login
    fi
    echo "Not authenticated with Azure. Attempting to authenticate..."
fi

#check if user has selected the correct subscription
currentSubscriptionId=$(az account show --query id -o tsv)
currentSubscriptionName=$(az account show --query name -o tsv)
if [ "$currentSubscriptionId" != "$azSubscriptionId" ]; then
    echo "Current selected subscription is $currentSubscriptionName ( $currentSubscriptionId )."
    read -rp "Do you want to continue with this subscription?(y/n): " confirmation
    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        echo "Fetching available subscriptions..."
        availableSubscriptions=$(az account list --query "[?state=='Enabled'].[name,id]" --output tsv)
        while true; do
            echo ""
            echo "Available Subscriptions:"
            echo "========================"
            echo "$availableSubscriptions" | awk '{printf "%d. %s ( %s )\n", NR, $1, $2}'
            echo "========================"
            echo ""
            read -rp "Enter the number of the subscription (1-$(echo "$availableSubscriptions" | wc -l)) to use: " subscriptionIndex
            if [[ "$subscriptionIndex" =~ ^[0-9]+$ ]] && [ "$subscriptionIndex" -ge 1 ] && [ "$subscriptionIndex" -le $(echo "$availableSubscriptions" | wc -l) ]; then
                selectedSubscription=$(echo "$availableSubscriptions" | sed -n "${subscriptionIndex}p")
                selectedSubscriptionName=$(echo "$selectedSubscription" | cut -f1)
                selectedSubscriptionId=$(echo "$selectedSubscription" | cut -f2)

                # Set the selected subscription
                if  az account set --subscription "$selectedSubscriptionId"; then
                    echo "Switched to subscription: $selectedSubscriptionName ( $selectedSubscriptionId )"
                    break
                else
                    echo "Failed to switch to subscription: $selectedSubscriptionName ( $selectedSubscriptionId )."
                fi
            else
                echo "Invalid selection. Please try again."
            fi
        done
    else
        echo "Proceeding with the current subscription: $currentSubscriptionName ( $currentSubscriptionId )"
        az account set --subscription "$currentSubscriptionId"
    fi
else
    echo "Proceeding with the subscription: $currentSubscriptionName ( $currentSubscriptionId )"
    az account set --subscription "$currentSubscriptionId"
fi

# Call add_cosmosdb_access.sh
echo "Running add_cosmosdb_access.sh"
bash infra/scripts/add_cosmosdb_access.sh "$resourceGroupName" "$cosmosDbAccountName" "$managedIdentityClientId"
if [ $? -ne 0 ]; then
    echo "Error: add_cosmosdb_access.sh failed."
    exit 1
fi
echo "add_cosmosdb_access.sh completed successfully."

# Call copy_kb_files.sh
echo "Running copy_kb_files.sh"
bash infra/scripts/copy_kb_files.sh "$storageAccount" "$fileSystem" "$managedIdentityClientId"
if [ $? -ne 0 ]; then
    echo "Error: copy_kb_files.sh failed."
    exit 1
fi
echo "copy_kb_files.sh completed successfully."

# Call run_create_index_scripts.sh
echo "Running run_create_index_scripts.sh"
bash infra/scripts/run_create_index_scripts.sh "$keyvaultName" "$resourceGroupName" "$aiFoundryName" "$aiSearchName" "$managedIdentityClientId"
if [ $? -ne 0 ]; then
    echo "Error: run_create_index_scripts.sh failed."
    exit 1
fi
echo "run_create_index_scripts.sh completed successfully."

echo "All scripts executed successfully."
