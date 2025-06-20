// ========== main.bicep ========== //
targetScope = 'resourceGroup'

@minLength(3)
@maxLength(20)
@description('A unique prefix for all resources in this deployment. This should be 3-20 characters long:')
param environmentName string

@metadata({
  azd: {
    type: 'location'
  }
})


@minLength(1)
@description('Secondary location for databases creation(example:eastus2):')
param secondaryLocation string

@minLength(1)
@description('GPT model deployment type:')
@allowed([
  'Standard'
  'GlobalStandard'
])
param deploymentType string = 'GlobalStandard'

@description('Name of the GPT model to deploy:')
param gptModelName string = 'gpt-4.1'

@description('Version of the GPT model to deploy:')
param gptModelVersion string = '2025-04-14'

param azureOpenaiAPIVersion string = '2024-05-01-preview'

@minValue(10)
@description('Capacity of the GPT deployment:')
// You can increase this, but capacity is limited per model/region, so you will get errors if you go over
// https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
param gptDeploymentCapacity int = 30

@minLength(1)
@description('Name of the Text Embedding model to deploy:')
@allowed([
  'text-embedding-ada-002'
])
param embeddingModel string = 'text-embedding-ada-002'

var abbrs = loadJsonContent('./abbreviations.json')
@minValue(10)
@description('Capacity of the Embedding Model deployment')
param embeddingDeploymentCapacity int = 80

param imageTag string = 'latest'
param AZURE_LOCATION string=''

@description('Optional: Existing Log Analytics Workspace Resource ID')
param existingLogAnalyticsWorkspaceId string = ''

var solutionLocation = empty(AZURE_LOCATION) ? resourceGroup().location : AZURE_LOCATION

var uniqueId = toLower(uniqueString(environmentName, subscription().id, solutionLocation))
var solutionPrefix = 'dg${padLeft(take(uniqueId, 12), 12, '0')}'


// ========== Managed Identity ========== //
module managedIdentityModule 'deploy_managed_identity.bicep' = {
  name: 'deploy_managed_identity'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    miName: '${abbrs.security.managedIdentity}${solutionPrefix}'
  }
  scope: resourceGroup(resourceGroup().name)
}

// ==========Key Vault Module ========== //
module kvault 'deploy_keyvault.bicep' = {
  name: 'deploy_keyvault'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
    keyvaultName:'${abbrs.security.keyVault}${solutionPrefix}'
  }
  scope: resourceGroup(resourceGroup().name)
}

// ==========AI Foundry and related resources ========== //
module aifoundry 'deploy_ai_foundry.bicep' = {
  name: 'deploy_ai_foundry'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    keyVaultName: kvault.outputs.keyvaultName
    deploymentType: deploymentType
    gptModelName: gptModelName
    gptModelVersion: gptModelVersion
    azureOpenaiAPIVersion: azureOpenaiAPIVersion
    gptDeploymentCapacity: gptDeploymentCapacity
    embeddingModel: embeddingModel
    embeddingDeploymentCapacity: embeddingDeploymentCapacity
    managedIdentityObjectId: managedIdentityModule.outputs.managedIdentityOutput.objectId
    existingLogAnalyticsWorkspaceId: existingLogAnalyticsWorkspaceId
  }
  scope: resourceGroup(resourceGroup().name)
}

// ========== Storage account module ========== //
module storageAccount 'deploy_storage_account.bicep' = {
  name: 'deploy_storage_account'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    keyVaultName: kvault.outputs.keyvaultName
    managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
    saName:'${abbrs.storage.storageAccount}${ solutionPrefix}' 
  }
  scope: resourceGroup(resourceGroup().name)
}


//========== Updates to Key Vault ========== //
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: aifoundry.outputs.keyvaultName
  scope: resourceGroup(resourceGroup().name)
}

//========== App service module ========== //
module appserviceModule 'deploy_app_service.bicep' = {
  name: 'deploy_app_service'
  params: {
    imageTag: imageTag
    applicationInsightsId: aifoundry.outputs.applicationInsightsId
    // identity:managedIdentityModule.outputs.managedIdentityOutput.id
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    aiSearchService: aifoundry.outputs.aiSearchService
    AzureSearchKey: keyVault.getSecret('AZURE-SEARCH-KEY')
    AzureOpenAIEndpoint:aifoundry.outputs.aoaiEndpoint
    AzureOpenAIModel: gptModelName 
    azureOpenAIApiVersion: azureOpenaiAPIVersion //'2024-02-15-preview'
    azureOpenaiResource:aifoundry.outputs.aiFoundryName
    aiFoundryProjectName: aifoundry.outputs.aiFoundryProjectName
    aiFoundryName: aifoundry.outputs.aiFoundryName
    aiFoundryProjectEndpoint: aifoundry.outputs.aiFoundryProjectEndpoint
    USE_CHAT_HISTORY_ENABLED:'True'
    AZURE_COSMOSDB_ACCOUNT: cosmosDBModule.outputs.cosmosAccountName
    // AZURE_COSMOSDB_ACCOUNT_KEY: keyVault.getSecret('AZURE-COSMOSDB-ACCOUNT-KEY')
    AZURE_COSMOSDB_CONVERSATIONS_CONTAINER: cosmosDBModule.outputs.cosmosContainerName
    AZURE_COSMOSDB_DATABASE: cosmosDBModule.outputs.cosmosDatabaseName
    appInsightsConnectionString: aifoundry.outputs.applicationInsightsConnectionString 
    AZURE_COSMOSDB_ENABLE_FEEDBACK:'True'
    HostingPlanName:'${abbrs.compute.appServicePlan}${solutionPrefix}'
    WebsiteName:'${abbrs.compute.webApp}${solutionPrefix}'
    useAiFoundrySdk: 'False'
  }
  scope: resourceGroup(resourceGroup().name)
  // dependsOn:[sqlDBModule]
}

output WEB_APP_URL string = appserviceModule.outputs.webAppUrl

// ========== Cosmos DB module ========== //
module cosmosDBModule 'deploy_cosmos_db.bicep' = {
  name: 'deploy_cosmos_db'
  params: {
    solutionName: solutionPrefix
    solutionLocation: secondaryLocation
    keyVaultName: kvault.outputs.keyvaultName
    accountName: '${abbrs.databases.cosmosDBDatabase}${solutionPrefix}'
  }
  scope: resourceGroup(resourceGroup().name)
}

output STORAGE_ACCOUNT_NAME string = storageAccount.outputs.storageName
output STORAGE_CONTAINER_NAME string = storageAccount.outputs.storageContainer
output KEY_VAULT_NAME string = kvault.outputs.keyvaultName
output COSMOSDB_ACCOUNT_NAME string = cosmosDBModule.outputs.cosmosAccountName
output RESOURCE_GROUP_NAME string = resourceGroup().name
output AI_FOUNDRY_NAME string = aifoundry.outputs.aiFoundryName
