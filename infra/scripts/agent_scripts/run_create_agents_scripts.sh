#!/bin/bash
set -e

echo "Started the agent creation script setup..."

# Variables - Can be provided as arguments or retrieved from azd env/deployment
resourceGroupName="$1"
projectEndpoint="$2"
solutionName="$3"
gptModelName="$4"
aiFoundryResourceId="$5"
azureAiSearchConnectionName="$6"
browseIndexName="$7"
templatesIndexName="$8"
sectionsIndexName="$9"

# Global variables to track original network access states for AI Foundry
original_foundry_public_access=""
aif_resource_group=""
aif_account_resource_id=""

# Check if azd is installed
check_azd_installed() {
	if command -v azd &> /dev/null; then
		return 0
	else
		return 1
	fi
}

# Function to get parameters from azd env if not provided
get_values_from_azd_env() {
	echo "Getting values from azd environment..."
	# Use grep with a regex to ensure we're only capturing sanitized values to avoid command injection
	projectEndpoint=$(azd env get-value AZURE_AI_AGENT_ENDPOINT 2>&1 | grep -E '^https?://[a-zA-Z0-9._/:/-]+$')
	solutionName=$(azd env get-value AZURE_ENV_NAME 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	gptModelName=$(azd env get-value AZURE_OPENAI_DEPLOYMENT_MODEL 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	aiFoundryResourceId=$(azd env get-value AI_FOUNDRY_RESOURCE_ID 2>&1 | grep -E '^[a-zA-Z0-9._/-]+$')
	azureAiSearchConnectionName=$(azd env get-value AZURE_AI_SEARCH_CONNECTION_NAME 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	browseIndexName=$(azd env get-value BROWSE_INDEX_NAME 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	templatesIndexName=$(azd env get-value TEMPLATES_INDEX_NAME 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	sectionsIndexName=$(azd env get-value SECTIONS_INDEX_NAME 2>&1 | grep -E '^[a-zA-Z0-9._-]+$')
	
	# Validate that we extracted all required values
	if [ -z "$projectEndpoint" ] || [ -z "$solutionName" ] || [ -z "$gptModelName" ] || [ -z "$aiFoundryResourceId" ] || [ -z "$azureAiSearchConnectionName" ] || [ -z "$browseIndexName" ] || [ -z "$templatesIndexName" ] || [ -z "$sectionsIndexName" ]; then
		echo "Error: One or more required values could not be retrieved from azd environment."
		return 1
	fi
	return 0
}

# Function to get parameters from deployment outputs
get_values_from_az_deployment() {
	echo "Getting values from Azure deployment outputs..."
	
	deploymentName=$(az group show --name "$resourceGroupName" --query "tags.DeploymentName" -o tsv)
	echo "Deployment Name (from tag): $deploymentName"
	
	echo "Fetching deployment outputs..."
	# Get all outputs
	deploymentOutputs=$(az deployment group show \
		--name "$deploymentName" \
		--resource-group "$resourceGroupName" \
		--query "properties.outputs" -o json)
	
	# Helper function to extract value from deployment outputs
	# Usage: extract_value "primaryKey" "fallbackKey"
	extract_value() {
		local primary_key="$1"
		local fallback_key="$2"
		local value
		
		value=$(echo "$deploymentOutputs" | grep -A 3 "\"$primary_key\"" | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
		if [ -z "$value" ] && [ -n "$fallback_key" ]; then
			value=$(echo "$deploymentOutputs" | grep -A 3 "\"$fallback_key\"" | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
		fi
		echo "$value"
	}
	
	# Extract each value using the helper function
	projectEndpoint=$(extract_value "azureAiAgentEndpoint" "azurE_AI_AGENT_ENDPOINT")
	solutionName=$(extract_value "solutionName" "solutioN_NAME")
	gptModelName=$(extract_value "azureOpenAIDeploymentModel" "azurE_OPENAI_DEPLOYMENT_MODEL")
	aiFoundryResourceId=$(extract_value "aiFoundryResourceId" "aI_FOUNDRY_RESOURCE_ID")
	azureAiSearchConnectionName=$(extract_value "azureAiSearchConnectionName" "azurE_AI_SEARCH_CONNECTION_NAME")
	browseIndexName=$(extract_value "browseIndexName" "browsE_INDEX_NAME")
	templatesIndexName=$(extract_value "templatesIndexName" "templateS_INDEX_NAME")
	sectionsIndexName=$(extract_value "sectionsIndexName" "sectionS_INDEX_NAME")
	
	# Define required values with their display names for error reporting
	declare -A required_values=(
		["projectEndpoint"]="AZURE_AI_AGENT_ENDPOINT"
		["solutionName"]="SOLUTION_NAME"
		["gptModelName"]="AZURE_OPENAI_DEPLOYMENT_MODEL"
		["aiFoundryResourceId"]="AI_FOUNDRY_RESOURCE_ID"
		["azureAiSearchConnectionName"]="AZURE_AI_SEARCH_CONNECTION_NAME"
		["browseIndexName"]="BROWSE_INDEX_NAME"
		["templatesIndexName"]="TEMPLATES_INDEX_NAME"
		["sectionsIndexName"]="SECTIONS_INDEX_NAME"
	)
	
	# Validate and collect missing values
	missing_values=()
	for var_name in "${!required_values[@]}"; do
		if [ -z "${!var_name}" ]; then
			missing_values+=("${required_values[$var_name]}")
		fi
	done
	
	if [ ${#missing_values[@]} -gt 0 ]; then
		echo "Error: The following required values could not be retrieved from Azure deployment outputs:"
		printf '  - %s\n' "${missing_values[@]}" | sort
		return 1
	fi
	return 0
}

# Function to enable public network access temporarily for AI Foundry
enable_foundry_public_access() {
	if [ -n "$aiFoundryResourceId" ] && [ "$aiFoundryResourceId" != "null" ]; then
		aif_account_resource_id="$aiFoundryResourceId"
		aif_resource_name=$(echo "$aiFoundryResourceId" | sed -n 's|.*/providers/Microsoft.CognitiveServices/accounts/\([^/]*\).*|\1|p')
		aif_resource_group=$(echo "$aiFoundryResourceId" | sed -n 's|.*/resourceGroups/\([^/]*\)/.*|\1|p')
		aif_subscription_id=$(echo "$aif_account_resource_id" | sed -n 's|.*/subscriptions/\([^/]*\)/.*|\1|p')
		
		original_foundry_public_access=$(az cognitiveservices account show \
			--name "$aif_resource_name" \
			--resource-group "$aif_resource_group" \
			--subscription "$aif_subscription_id" \
			--query "properties.publicNetworkAccess" \
			--output tsv)
		
		if [ -z "$original_foundry_public_access" ] || [ "$original_foundry_public_access" = "null" ]; then
			echo "⚠ Could not retrieve AI Foundry network access status"
		elif [ "$original_foundry_public_access" != "Enabled" ]; then
			echo "✓ Enabling AI Foundry public access"
			if ! MSYS_NO_PATHCONV=1 az resource update \
				--ids "$aif_account_resource_id" \
				--api-version 2024-10-01 \
				--set properties.publicNetworkAccess=Enabled properties.apiProperties="{}" \
				--output none; then
				echo "⚠ Failed to enable AI Foundry public access"
			fi
			# Wait a bit for changes to take effect
			sleep 10
		fi
	fi
	return 0
}

# Function to restore original network access settings for AI Foundry
restore_foundry_network_access() {
	if [ -n "$original_foundry_public_access" ] && [ "$original_foundry_public_access" != "Enabled" ]; then
		echo "✓ Restoring AI Foundry access"
		if ! MSYS_NO_PATHCONV=1 az resource update \
			--ids "$aif_account_resource_id" \
			--api-version 2024-10-01 \
			--set properties.publicNetworkAccess="$original_foundry_public_access" \
			--set properties.apiProperties.qnaAzureSearchEndpointKey="" \
			--set properties.networkAcls.bypass="AzureServices" \
			--output none 2>/dev/null; then
			echo "⚠ Failed to restore AI Foundry access - please check Azure portal"
		fi
	fi
}

# Function to handle script cleanup on exit
cleanup_on_exit() {
	exit_code=$?
	echo ""
	if [ $exit_code -ne 0 ]; then
		echo "❌ Script failed"
	else
		echo "✅ Script completed successfully"
	fi
	restore_foundry_network_access
	exit $exit_code
}

# Register cleanup function
trap cleanup_on_exit EXIT

# Determine how to get values
if [ -z "$resourceGroupName" ]; then
	# No resource group provided - use azd env
	if check_azd_installed; then
		if ! get_values_from_azd_env; then
			echo "Failed to get values from azd environment."
			echo ""
			echo "If you want to use deployment outputs instead, please provide the resource group name as the first argument."
			echo "Usage: $0 [resourceGroupName] or $0 <resourceGroupName> <projectEndpoint> <solutionName> <gptModelName> <aiFoundryResourceId> <azureAiSearchConnectionName> <browseIndexName> <templatesIndexName> <sectionsIndexName>"
			exit 1
		fi
	else
		echo "Error: Parameters not provided and azd is not installed."
		echo "Usage: $0 [resourceGroupName] or provide all parameters"
		exit 1
	fi
else
	# Resource group provided - check if all parameters provided or get from deployment
	if [ -z "$projectEndpoint" ]; then
		# Resource group provided but other params missing - get from deployment
		echo "Resource group provided: $resourceGroupName"
		if ! get_values_from_az_deployment; then
			echo "Failed to get values from deployment outputs."
			echo ""
			echo "Please provide all parameters explicitly."
			echo "Usage: $0 <resourceGroupName> <projectEndpoint> <solutionName> <gptModelName> <aiFoundryResourceId> <azureAiSearchConnectionName> <browseIndexName> <templatesIndexName> <sectionsIndexName>"
			exit 1
		fi
	fi
fi

# Final validation
if [ -z "$projectEndpoint" ] || [ -z "$solutionName" ] || [ -z "$gptModelName" ] || [ -z "$aiFoundryResourceId" ] || [ -z "$azureAiSearchConnectionName" ] || [ -z "$browseIndexName" ] || [ -z "$templatesIndexName" ] || [ -z "$sectionsIndexName" ]; then
	echo "Error: Missing required parameters after attempting to retrieve them."
	echo "Usage: $0 [resourceGroupName] or provide all parameters"
	exit 1
fi

echo ""
echo "==============================================="
echo "Values to be used:"
echo "==============================================="
echo "Project Endpoint: $projectEndpoint"
echo "Solution Name: $solutionName"
echo "GPT Model Name: $gptModelName"
echo "AI Foundry Resource ID: $aiFoundryResourceId"
echo "Azure AI Search Connection Name: $azureAiSearchConnectionName"
echo "Browse Index Name: $browseIndexName"
echo "Templates Index Name: $templatesIndexName"
echo "Sections Index Name: $sectionsIndexName"
echo "==============================================="
echo ""

# Check if user is logged in to Azure
echo "Checking Azure authentication..."
if az account show &> /dev/null; then
    echo "Already authenticated with Azure."
else
    echo "Authenticating with Azure CLI..."
    az login --use-device-code
fi

echo "Getting signed in user id"
signed_user_id=$(az ad signed-in-user show --query id -o tsv) || signed_user_id=${AZURE_CLIENT_ID}

echo "Checking if the user has Azure AI User role on the AI Foundry"
role_assignment=$(MSYS_NO_PATHCONV=1 az role assignment list \
  --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" \
  --scope "$aiFoundryResourceId" \
  --assignee "$signed_user_id" \
  --query "[].roleDefinitionId" -o tsv)

if [ -z "$role_assignment" ]; then
    echo "User does not have the Azure AI User role. Assigning the role..."
    MSYS_NO_PATHCONV=1 az role assignment create \
      --assignee "$signed_user_id" \
      --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" \
      --scope "$aiFoundryResourceId" \
      --output none
    
    if [ $? -ne 0 ]; then
        echo "Failed to assign Azure AI User role"
        exit 1
    fi
    
    echo "Role assigned successfully. Waiting for role assignment to propagate..."
    sleep 15
else
    echo "User already has Azure AI User role."
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Enable public network access for AI Foundry
enable_foundry_public_access

# Install requirements
echo "Installing Python requirements..."
pip install -r "${SCRIPT_DIR}/requirements.txt" --quiet

# Run agent creation script and capture output
echo "Creating agents..."
eval $(python "${SCRIPT_DIR}/01_create_agents.py" \
  --ai_project_endpoint="$projectEndpoint" \
  --solution_name="$solutionName" \
  --gpt_model_name="$gptModelName" \
  --azure_ai_search_connection_name="$azureAiSearchConnectionName" \
  --browse_index_name="$browseIndexName" \
  --templates_index_name="$templatesIndexName" \
  --sections_index_name="$sectionsIndexName")

echo "Agents creation completed."

# Set azd environment variables
if [ -n "$browseAgentName" ]; then
    azd env set AGENT_NAME_BROWSE "$browseAgentName"
    echo "Set AGENT_NAME_BROWSE=$browseAgentName"
fi

if [ -n "$templateAgentName" ]; then
    azd env set AGENT_NAME_TEMPLATE "$templateAgentName"
    echo "Set AGENT_NAME_TEMPLATE=$templateAgentName"
fi

if [ -n "$sectionAgentName" ]; then
    azd env set AGENT_NAME_SECTION "$sectionAgentName"
    echo "Set AGENT_NAME_SECTION=$sectionAgentName"
fi

echo "Environment variables updated successfully!"
