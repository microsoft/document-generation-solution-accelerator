// Creates Azure dependent resources for Azure AI studio

@minLength(3)
@maxLength(15)
@description('Solution Name')
param solutionName string

@description('Solution Location')
param solutionLocation string

@description('Contains Name of KeyVault.')
param keyVaultName string

@description('Indicates the type of Deployment.')
param deploymentType string

@description('GPT Model Name')
param gptModelName string

@description('GPT Model Version.')
param gptModelVersion string

@description('Azure OepnAI API Version.')
param azureOpenaiAPIVersion string

@description('Param to get Deployment Capacity.')
param gptDeploymentCapacity int

@description('Embedding Model.')
param embeddingModel string

@description('Info about Embedding Deployment Capacity.')
param embeddingDeploymentCapacity int

@description('Managed Identity Object ID.')
param managedIdentityObjectId string

@description('Existing Log Analytics WorkspaceID.')
param existingLogAnalyticsWorkspaceId string = ''

@description('Azure Existing AI Project ResourceID.')
param azureExistingAIProjectResourceId string = ''

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

//var abbrs = loadJsonContent('./abbreviations.json')

var aiFoundryName = 'aif-${solutionName}'
var applicationInsightsName = 'appi-${solutionName}'
var keyvaultName = 'kv-${solutionName}'
var location = solutionLocation //'eastus2'
var aiProjectName = 'proj-${solutionName}'
var aiProjectFriendlyName = aiProjectName
var aiProjectDescription = 'AI Foundry Project'
var aiSearchName = 'srch-${solutionName}'
var workspaceName = 'log-${solutionName}'
// var aiSearchConnectionName = 'myVectorStoreProjectConnectionName-${solutionName}'

var useExisting = !empty(existingLogAnalyticsWorkspaceId)
var existingLawSubscription = useExisting ? split(existingLogAnalyticsWorkspaceId, '/')[2] : ''
var existingLawResourceGroup = useExisting ? split(existingLogAnalyticsWorkspaceId, '/')[4] : ''
var existingLawName = useExisting ? split(existingLogAnalyticsWorkspaceId, '/')[8] : ''

var existingOpenAIEndpoint = !empty(azureExistingAIProjectResourceId)
  ? format('https://{0}.openai.azure.com/', split(azureExistingAIProjectResourceId, '/')[8])
  : ''
var existingProjEndpoint = !empty(azureExistingAIProjectResourceId)
  ? format(
      'https://{0}.services.ai.azure.com/api/projects/{1}',
      split(azureExistingAIProjectResourceId, '/')[8],
      split(azureExistingAIProjectResourceId, '/')[10]
    )
  : ''
var existingAIFoundryName = !empty(azureExistingAIProjectResourceId)
  ? split(azureExistingAIProjectResourceId, '/')[8]
  : ''
var existingAIProjectName = !empty(azureExistingAIProjectResourceId)
  ? split(azureExistingAIProjectResourceId, '/')[10]
  : ''
var existingAIServiceSubscription = !empty(azureExistingAIProjectResourceId)
  ? split(azureExistingAIProjectResourceId, '/')[2]
  : ''
var existingAIServiceResourceGroup = !empty(azureExistingAIProjectResourceId)
  ? split(azureExistingAIProjectResourceId, '/')[4]
  : ''
var aiSearchConnectionName = 'foundry-search-connection-${solutionName}'
var aiAppInsightConnectionName = 'foundry-app-insights-connection-${solutionName}'

var aiModelDeployments = [
  {
    name: gptModelName
    model: gptModelName
    sku: {
      name: deploymentType
      capacity: gptDeploymentCapacity
    }
    version: gptModelVersion
    raiPolicyName: 'Microsoft.Default'
  }
  {
    name: embeddingModel
    model: embeddingModel
    sku: {
      name: 'GlobalStandard'
      capacity: embeddingDeploymentCapacity
    }
    version: '2'
    raiPolicyName: 'Microsoft.Default'
  }
]

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource existingLogAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-08-01' existing = if (useExisting) {
  name: existingLawName
  scope: resourceGroup(existingLawSubscription, existingLawResourceGroup)
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if (!useExisting) {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
  }
  tags : tags
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    WorkspaceResourceId: useExisting ? existingLogAnalyticsWorkspace.id : logAnalytics.id
  }
  tags : tags
}

resource existingAiFoundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = if (!empty(azureExistingAIProjectResourceId)) {
  name: existingAIFoundryName
  scope: resourceGroup(existingAIServiceSubscription, existingAIServiceResourceGroup)
}

resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = if (empty(azureExistingAIProjectResourceId))  {
  name: aiFoundryName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
  tags : tags
}

resource aiFoundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = if (empty(azureExistingAIProjectResourceId))   {
  parent: aiFoundry
  name: aiProjectName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: aiProjectDescription
    displayName: aiProjectFriendlyName
  }
  tags : tags
}

@batchSize(1)
resource aiFModelDeployments 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = [
  for aiModeldeployment in aiModelDeployments: if (empty(azureExistingAIProjectResourceId))   {
    parent: aiFoundry
    name: aiModeldeployment.name
    properties: {
      model: {
        format: 'OpenAI'
        name: aiModeldeployment.model
      }
      raiPolicyName: aiModeldeployment.raiPolicyName
    }
    sku: {
      name: aiModeldeployment.sku.name
      capacity: aiModeldeployment.sku.capacity
    }
    tags : tags
  }
]

resource aiSearch 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: aiSearchName
  location: solutionLocation
  sku: {
    name: 'basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    disableLocalAuth: true
    semanticSearch: 'free'
  }
  tags : tags
}

resource aiSearchFoundryConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = if (empty(azureExistingAIProjectResourceId))   {
  name: aiSearchConnectionName
  parent: aiFoundryProject
  properties: {
    category: 'CognitiveSearch'
    target: 'https://${aiSearchName}.search.windows.net'
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiSearch.id
      location: aiSearch.location
    }
  }
}

module existing_AIProject_SearchConnectionModule 'deploy_aifp_aisearch_connection.bicep' = if (!empty(azureExistingAIProjectResourceId)) {
  name: 'aiProjectSearchConnectionDeployment'
  scope: resourceGroup(existingAIServiceSubscription, existingAIServiceResourceGroup)
  params: {
    existingAIProjectName: existingAIProjectName
    existingAIFoundryName: existingAIFoundryName
    aiSearchName: aiSearchName
    aiSearchResourceId: aiSearch.id
    aiSearchLocation: aiSearch.location
    aiSearchConnectionName: aiSearchConnectionName
    tags : tags
  }
}

resource cognitiveServicesOpenAIUser 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  name: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
}

module assignOpenAIRoleToAISearch 'deploy_foundry_role_assignment.bicep' = {
  name: 'assignOpenAIRoleToAISearch'
  scope: resourceGroup(existingAIServiceSubscription, existingAIServiceResourceGroup)
  params: {
    roleDefinitionId: cognitiveServicesOpenAIUser.id
    roleAssignmentName: guid(resourceGroup().id, aiSearch.id, cognitiveServicesOpenAIUser.id, 'openai-foundry')
    aiFoundryName: !empty(azureExistingAIProjectResourceId) ? existingAIFoundryName : aiFoundryName
    aiProjectName: !empty(azureExistingAIProjectResourceId) ? existingAIProjectName : aiProjectName
    principalId: aiSearch.identity.principalId
    aiModelDeployments: aiModelDeployments
    tags : tags
  }
}

@description('This is the built-in Search Index Data Reader role.')
resource searchIndexDataReaderRoleDefinition 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: aiSearch
  name: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
}

resource searchIndexDataReaderRoleAssignmentToAIFP 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (empty(azureExistingAIProjectResourceId)) {
  name: guid(aiSearch.id, aiFoundryProject.id, searchIndexDataReaderRoleDefinition.id)
  scope: aiSearch
  properties: {
    roleDefinitionId: searchIndexDataReaderRoleDefinition.id
    principalId: aiFoundryProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
resource assignSearchIndexDataReaderToExistingAiProject 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(azureExistingAIProjectResourceId)) {
  name: guid(resourceGroup().id, existingAIProjectName, searchIndexDataReaderRoleDefinition.id, 'Existing')
  scope: aiSearch
  properties: {
    roleDefinitionId: searchIndexDataReaderRoleDefinition.id
    principalId: assignOpenAIRoleToAISearch.outputs.aiProjectPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('This is the built-in Search Service Contributor role.')
resource searchServiceContributorRoleDefinition 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: aiSearch
  name: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
}

resource searchServiceContributorRoleAssignmentToAIFP 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (empty(azureExistingAIProjectResourceId)) {
  name: guid(aiSearch.id, aiFoundryProject.id, searchServiceContributorRoleDefinition.id)
  scope: aiSearch
  properties: {
    roleDefinitionId: searchServiceContributorRoleDefinition.id
    principalId: aiFoundryProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource searchServiceContributorRoleAssignmentExisting 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(azureExistingAIProjectResourceId)) {
  name: guid(resourceGroup().id, existingAIProjectName, searchServiceContributorRoleDefinition.id, 'Existing')
  scope: aiSearch
  properties: {
    roleDefinitionId: searchServiceContributorRoleDefinition.id
    principalId: assignOpenAIRoleToAISearch.outputs.aiProjectPrincipalId
    principalType: 'ServicePrincipal'
  }
}


resource tenantIdEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'TENANT-ID'
  properties: {
    value: subscription().tenantId
  }
  tags : tags
}


resource azureOpenAIDeploymentModel 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-OPEN-AI-DEPLOYMENT-MODEL'
  properties: {
    value: gptModelName
  }
  tags : tags
}

resource azureOpenAIApiVersionEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-OPENAI-PREVIEW-API-VERSION'
  properties: {
    value: azureOpenaiAPIVersion //'2024-02-15-preview'
  }
  tags : tags
}

resource azureOpenAIEndpointEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-OPENAI-ENDPOINT'
  properties: {
     value: !empty(existingOpenAIEndpoint)
      ? existingOpenAIEndpoint
      : aiFoundry.properties.endpoints['OpenAI Language Model Instance API']
  }
  tags : tags
  }

resource azureOpenAIEmbeddingDeploymentModel 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-OPENAI-EMBEDDING-MODEL'
  properties: {
    value: embeddingModel
  }
  tags : tags
}

resource azureSearchServiceEndpointEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-SEARCH-ENDPOINT'
  properties: {
    value: 'https://${aiSearch.name}.search.windows.net'
  }
  tags : tags
}

resource azureSearchServiceEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-SEARCH-SERVICE'
  properties: {
    value: aiSearch.name
  }
  tags : tags
}

resource azureSearchIndexEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-SEARCH-INDEX'
  properties: {
    value: 'pdf_index'
  }
  tags : tags
}

resource cogServiceEndpointEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'COG-SERVICES-ENDPOINT'
  properties: {
    value: !empty(existingOpenAIEndpoint)
      ? existingOpenAIEndpoint
      : aiFoundry.properties.endpoint
  }
  tags : tags
}

resource cogServiceKeyEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'COG-SERVICES-KEY'
  properties: {
    value: !empty(existingOpenAIEndpoint)
      ? existingAiFoundry.listKeys().key1
      : aiFoundry.listKeys().key1
  }
  tags : tags
}

resource cogServiceNameEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'COG-SERVICES-NAME'
  properties: {
    value: !empty(existingAIFoundryName) ? existingAIFoundryName : aiFoundryName
  }
  tags : tags
}

resource azureSubscriptionIdEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-SUBSCRIPTION-ID'
  properties: {
    value: subscription().subscriptionId
  }
  tags : tags
}

resource resourceGroupNameEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-RESOURCE-GROUP'
  properties: {
    value: resourceGroup().name
  }
  tags : tags
}

resource azureLocatioEntry 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'AZURE-LOCATION'
  properties: {
    value: solutionLocation
  }
  tags : tags
}

@description('Contains Name of KeyVault.')
output keyvaultName string = keyvaultName

@description('Contains KeyVault ID.')
output keyvaultId string = keyVault.id

// output aiServicesTarget string = aiFoundry.properties.endpoint //aiServices_m.properties.endpoint
// output aiServicesName string = aiFoundryName //aiServicesName_m
// output aiServicesId string = aiFoundry.id //aiServices_m.id

@description('Contains AI Search Name.')
output aiSearchName string = aiSearchName

@description('Contains AI SearchID.')
output aiSearchId string = aiSearch.id

@description('Contains AI Search Target.')
output aiSearchTarget string = 'https://${aiSearch.name}.search.windows.net'

@description('Contains AI Search Service.')
output aiSearchService string = aiSearch.name

@description('Contains Name of AI Search Connection.')
output aiSearchConnectionName string = aiSearchConnectionName

@description('Contains Name of AI Foundry Project.')
output aiFoundryProjectName string = !empty(existingAIProjectName) ? existingAIProjectName : aiFoundryProject.name
// output aiFoundryProjectEndpoint string = aiFoundryProject.properties.endpoints['AI Foundry API']

@description('Contains Name of AI Foundry Project Endpoint.')
output aiFoundryProjectEndpoint string = !empty(existingProjEndpoint)
  ? existingProjEndpoint
  : aiFoundryProject.properties.endpoints['AI Foundry API']
// output aoaiEndpoint string = aiFoundry.properties.endpoints['OpenAI Language Model Instance API']

@description('Contains AI Endpoint.')
output aoaiEndpoint string = !empty(existingOpenAIEndpoint)
  ? existingOpenAIEndpoint
  : aiFoundry.properties.endpoints['OpenAI Language Model Instance API']

@description('Contains Name of AI Foundry.')  
output aiFoundryName string = !empty(existingAIFoundryName) ? existingAIFoundryName : aiFoundryName

@description('Contains Name of AI Foundry RG.')
output aiFoundryRgName string = !empty(existingAIServiceResourceGroup) ? existingAIServiceResourceGroup : resourceGroup().name

@description('Contains Application Insights ID.')
output applicationInsightsId string = applicationInsights.id

@description('Contains Log Analytics Workspace Resource Name.')
output logAnalyticsWorkspaceResourceName string = useExisting ? existingLogAnalyticsWorkspace.name : logAnalytics.name

@description('Contains Application Insights Connection String.')
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString
