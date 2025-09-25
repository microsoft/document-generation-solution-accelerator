#!/bin/bash

# Variables
resourceGroupName="$1"

# Global variables to track original network access states
original_storage_public_access=""
original_storage_default_action=""
original_keyvault_public_access=""
original_foundry_public_access=""
aif_resource_group=""
aif_account_resource_id=""

# Function to enable public network access temporarily
enable_public_access() {
    echo "=== Temporarily enabling public network access for services ==="
    
    # Enable public access for Storage Account
    echo "Enabling public access for Storage Account: $storageAccount"
    original_storage_public_access=$(az storage account show \
        --name "$storageAccount" \
        --resource-group "$resourceGroupName" \
        --query "publicNetworkAccess" \
        -o tsv)
    original_storage_default_action=$(az storage account show \
        --name "$storageAccount" \
        --resource-group "$resourceGroupName" \
        --query "networkRuleSet.defaultAction" \
        -o tsv)
    
    if [ "$original_storage_public_access" != "Enabled" ]; then
        az storage account update \
            --name "$storageAccount" \
            --resource-group "$resourceGroupName" \
            --public-network-access Enabled \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Storage Account public access enabled"
        else
            echo "✗ Failed to enable Storage Account public access"
            return 1
        fi
    else
        echo "✓ Storage Account public access already enabled"
    fi
    
    # Also ensure the default network action allows access
    if [ "$original_storage_default_action" != "Allow" ]; then
        echo "Setting Storage Account network default action to Allow"
        az storage account update \
            --name "$storageAccount" \
            --resource-group "$resourceGroupName" \
            --default-action Allow \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Storage Account network default action set to Allow"
        else
            echo "✗ Failed to set Storage Account network default action"
            return 1
        fi
    else
        echo "✓ Storage Account network default action already set to Allow"
    fi

    # Enable public access for AI Foundry
    # Extract the account resource ID (remove /projects/... part if present)
    aif_account_resource_id=$(echo "$aif_resource_id" | sed 's|/projects/.*||')
    aif_resource_name=$(basename "$aif_account_resource_id")
    # Extract resource group from the AI Foundry account resource ID
    aif_resource_group=$(echo "$aif_account_resource_id" | sed -n 's|.*/resourceGroups/\([^/]*\)/.*|\1|p')
    
    original_foundry_public_access=$(az cognitiveservices account show \
        --name "$aif_resource_name" \
        --resource-group "$aif_resource_group" \
        --query "properties.publicNetworkAccess" \
        --output tsv)
    if [ -z "$original_foundry_public_access" ] || [ "$original_foundry_public_access" = "null" ]; then
        echo "⚠ Info: Could not retrieve AI Foundry network access status."
        echo "  AI Foundry network access might be managed differently."
    elif [ "$original_foundry_public_access" != "Enabled" ]; then
        echo "Current AI Foundry public access: $original_foundry_public_access"
        echo "Enabling public access for AI Foundry resource: $aif_resource_name (Resource Group: $aif_resource_group)"
        if MSYS_NO_PATHCONV=1 az resource update \
            --ids "$aif_account_resource_id" \
            --api-version 2024-10-01 \
            --set properties.publicNetworkAccess=Enabled \
            --set properties.apiProperties.qnaAzureSearchEndpointKey="" \
            --output none; then
            echo "✓ AI Foundry public access enabled"
        else
            echo "⚠ Warning: Failed to enable AI Foundry public access automatically."
        fi
    else
        echo "✓ AI Foundry public access already enabled"
    fi

    # Wait a bit for changes to take effect
    echo "Waiting for network access changes to propagate..."
    sleep 10
    
    # Enable public access for Key Vault
    echo "Enabling public access for Key Vault: $keyvaultName"
    original_keyvault_public_access=$(az keyvault show \
        --name "$keyvaultName" \
        --resource-group "$resourceGroupName" \
        --query "properties.publicNetworkAccess" \
        -o tsv)
    
    if [ "$original_keyvault_public_access" != "Enabled" ]; then
        az keyvault update \
            --name "$keyvaultName" \
            --resource-group "$resourceGroupName" \
            --public-network-access Enabled \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Key Vault public access enabled"
        else
            echo "✗ Failed to enable Key Vault public access"
            return 1
        fi
    else
        echo "✓ Key Vault public access already enabled"
    fi
    
    # Additional wait for all changes to propagate fully
    echo "Allowing additional time for all network access changes to propagate..."
    echo "Note: Changes may take up to 5 minutes to fully appear in Azure Portal"
    sleep 30
    echo "=== Public network access configuration completed ==="
    return 0
}

# Function to restore original network access settings
restore_network_access() {
    echo "=== Restoring original network access settings ==="
    
    # Restore Storage Account access
    if [ -n "$original_storage_public_access" ] && [ "$original_storage_public_access" != "Enabled" ]; then
        echo "Restoring Storage Account public access to: $original_storage_public_access"
        # Handle case sensitivity - convert to proper case
        case "$original_storage_public_access" in
            "enabled"|"Enabled") restore_value="Enabled" ;;
            "disabled"|"Disabled") restore_value="Disabled" ;;
            *) restore_value="$original_storage_public_access" ;;
        esac
        az storage account update \
            --name "$storageAccount" \
            --resource-group "$resourceGroupName" \
            --public-network-access "$restore_value" \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Storage Account access restored"
        else
            echo "✗ Failed to restore Storage Account access"
        fi
    else
        echo "Storage Account access unchanged (already at desired state)"
    fi
    
    # Restore Storage Account network default action
    if [ -n "$original_storage_default_action" ] && [ "$original_storage_default_action" != "Allow" ]; then
        echo "Restoring Storage Account network default action to: $original_storage_default_action"
        az storage account update \
            --name "$storageAccount" \
            --resource-group "$resourceGroupName" \
            --default-action "$original_storage_default_action" \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Storage Account network default action restored"
        else
            echo "✗ Failed to restore Storage Account network default action"
        fi
    else
        echo "Storage Account network default action unchanged (already at desired state)"
    fi
    
    # Restore Key Vault access
    if [ -n "$original_keyvault_public_access" ] && [ "$original_keyvault_public_access" != "Enabled" ]; then
        echo "Restoring Key Vault public access to: $original_keyvault_public_access"
        # Handle case sensitivity - convert to proper case
        case "$original_keyvault_public_access" in
            "enabled"|"Enabled") restore_value="Enabled" ;;
            "disabled"|"Disabled") restore_value="Disabled" ;;
            *) restore_value="$original_keyvault_public_access" ;;
        esac
        az keyvault update \
            --name "$keyvaultName" \
            --resource-group "$resourceGroupName" \
            --public-network-access "$restore_value" \
            --output none
        if [ $? -eq 0 ]; then
            echo "✓ Key Vault access restored"
        else
            echo "✗ Failed to restore Key Vault access"
        fi
    else
        echo "Key Vault access unchanged (already at desired state)"
    fi

    # Restore AI Foundry access
    if [ -n "$original_foundry_public_access" ] && [ "$original_foundry_public_access" != "Enabled" ]; then
        echo "Restoring AI Foundry public access to: $original_foundry_public_access"
        # Try using the working approach to restore the original setting
        if MSYS_NO_PATHCONV=1 az resource update \
            --ids "$aif_account_resource_id" \
            --api-version 2024-10-01 \
            --set properties.publicNetworkAccess="$original_foundry_public_access" \
            --set properties.apiProperties.qnaAzureSearchEndpointKey="" \
            --set properties.networkAcls.bypass="AzureServices" \
            --output none 2>/dev/null; then
            echo "✓ AI Foundry access restored"
        else
            echo "⚠ Warning: Failed to restore AI Foundry access automatically."
            echo "  Please manually restore network access in the Azure portal if needed."
        fi
    else
        echo "AI Foundry access unchanged (already at desired state)"
    fi
    
    echo "=== Network access restoration completed ==="
}

# Function to handle script cleanup on exit
cleanup_on_exit() {
    exit_code=$?
    echo ""
    if [ $exit_code -ne 0 ]; then
        echo "Script failed with exit code: $exit_code"
    fi
    echo "Performing cleanup..."
    restore_network_access
    exit $exit_code
}

# Set up trap to ensure cleanup happens on exit
trap cleanup_on_exit EXIT INT TERM
if az account show &> /dev/null; then
    echo "Already authenticated with Azure."
else
    echo "Authenticating with Azure CLI..."
    az login
    echo "Authenticated with Azure CLI."
fi
# get parameters from deployment
deploymentName=$(az group show --name "$resourceGroupName" --query "tags.DeploymentName" -o tsv) 
echo "Deployment Name (from tag): $deploymentName"
cosmosDbAccountName=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.cosmosdB_ACCOUNT_NAME.value" -o tsv)
storageAccount=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.storagE_ACCOUNT_NAME.value" -o tsv)
fileSystem=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.storagE_CONTAINER_NAME.value" -o tsv)
keyvaultName=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.keY_VAULT_NAME.value" -o tsv)
managedIdentityClientId=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.manageD_IDENTITY_CLIENT_ID.value" -o tsv)
aiSearchName=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.aI_SEARCH_SERVICE_NAME.value" -o tsv)
aif_resource_id=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.aI_FOUNDRY_RESOURCE_ID.value" -o tsv)
azSubscriptionId=$(az deployment group show \
    --name "$deploymentName" \
    --resource-group "$resourceGroupName" \
    --query "properties.outputs.subscriptionId.value" -o tsv)
# Check if all required arguments are provided
if [ -z "$storageAccount" ] || [ -z "$fileSystem" ] || [ -z "$keyvaultName" ] || [ -z "$cosmosDbAccountName" ] || [ -z "$resourceGroupName" ] || [ -z "$aif_resource_id" ] || [ -z "$aiSearchName" ]; then
    echo "Usage: $0 <storageAccount> <storageContainerName> <keyvaultName> <cosmosDbAccountName> <resourceGroupName> <aiSearchName> <managedIdentityClientId> <aif_resource_id>"
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

# Enable public network access for required services
enable_public_access
if [ $? -ne 0 ]; then
    echo "Error: Failed to enable public network access for services."
    exit 1
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
bash infra/scripts/run_create_index_scripts.sh "$keyvaultName" "$resourceGroupName" "$aiSearchName" "$managedIdentityClientId" "$aif_resource_id"
if [ $? -ne 0 ]; then
    echo "Error: run_create_index_scripts.sh failed."
    exit 1
fi
echo "run_create_index_scripts.sh completed successfully."

echo "All scripts executed successfully."
# Note: cleanup_on_exit will be called automatically via the trap
