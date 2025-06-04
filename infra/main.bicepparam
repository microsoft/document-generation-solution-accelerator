using './main.bicep'

param AZURE_LOCATION = readEnvironmentVariable('AZURE_LOCATION', '')
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'env_name')
param secondaryLocation = readEnvironmentVariable('AZURE_ENV_SECONDARY_LOCATION', 'eastus2')
param deploymentType = readEnvironmentVariable('AZURE_ENV_MODEL_DEPLOYMENT_TYPE', 'GlobalStandard')
param gptModelName = readEnvironmentVariable('AZURE_ENV_MODEL_NAME', 'gpt-4.1')
param gptModelVersion = readEnvironmentVariable('AZURE_ENV_MODEL_VERSION', '2025-04-14')
param gptDeploymentCapacity = int(readEnvironmentVariable('AZURE_ENV_MODEL_CAPACITY', '30'))

param embeddingDeploymentCapacity = int(readEnvironmentVariable('AZURE_ENV_EMBEDDING_MODEL_CAPACITY', '80'))
param existingLogAnalyticsWorkspaceId = readEnvironmentVariable('AZURE_ENV_LOG_ANALYTICS_WORKSPACE_ID', '')
