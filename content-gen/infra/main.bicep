// ========== main.bicep ========== //
targetScope = 'resourceGroup'

metadata name = 'Intelligent Content Generation Accelerator'
metadata description = '''Solution Accelerator for multimodal marketing content generation using Microsoft Agent Framework.
'''

@minLength(3)
@maxLength(15)
@description('Optional. A unique application/solution name for all resources in this deployment.')
param solutionName string = 'contentgen'

@maxLength(5)
@description('Optional. A unique text value for the solution.')
param solutionUniqueText string = substring(uniqueString(subscription().id, resourceGroup().name, solutionName), 0, 5)

@allowed([
  'australiaeast'
  'centralus'
  'eastasia'
  'eastus2'
  'japaneast'
  'northeurope'
  'southeastasia'
  'uksouth'
])
@metadata({ azd: { type: 'location' } })
@description('Required. Azure region for all services.')
param location string

@minLength(3)
@description('Optional. Secondary location for databases creation.')
param secondaryLocation string = 'uksouth'

@allowed([
  'australiaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'japaneast'
  'koreacentral'
  'swedencentral'
  'switzerlandnorth'
  'uaenorth'
  'uksouth'
  'westus'
  'westus3'
])
@description('Location for AI deployments.')
@metadata({
  azd: {
    type: 'location'
    usageName: [
      'OpenAI.GlobalStandard.gpt-5, 150'
      'OpenAI.GlobalStandard.dall-e-3, 10'
      'OpenAI.GlobalStandard.text-embedding-ada-002, 80'
    ]
  }
})
param azureAiServiceLocation string

@minLength(1)
@allowed([
  'Standard'
  'GlobalStandard'
])
@description('Optional. GPT model deployment type.')
param gptModelDeploymentType string = 'GlobalStandard'

@minLength(1)
@description('Optional. Name of the GPT model to deploy.')
param gptModelName string = 'gpt-5'

@description('Optional. Version of the GPT model to deploy.')
param gptModelVersion string = '2025-04-14'

@description('Optional. Name of the DALL-E model to deploy.')
param dalleModelName string = 'dall-e-3'

@description('Optional. Version of the DALL-E model.')
param dalleModelVersion string = '3.0'

@description('Optional. API version for Azure OpenAI service.')
param azureOpenaiAPIVersion string = '2025-01-01-preview'

@description('Optional. API version for Azure AI Agent service.')
param azureAiAgentApiVersion string = '2025-05-01'

@minValue(10)
@description('Optional. AI model deployment token capacity.')
param gptModelCapacity int = 150

@minValue(1)
@description('Optional. DALL-E model deployment capacity.')
param dalleModelCapacity int = 10

@minLength(1)
@description('Optional. Name of the Text Embedding model to deploy.')
param embeddingModel string = 'text-embedding-ada-002'

@minValue(10)
@description('Optional. Capacity of the Embedding Model deployment.')
param embeddingDeploymentCapacity int = 80

@description('Optional. Existing Log Analytics Workspace Resource ID.')
param existingLogAnalyticsWorkspaceId string = ''

@description('Optional. Resource ID of an existing Foundry project.')
param azureExistingAIProjectResourceId string = ''

@description('Optional. The tags to apply to all deployed Azure resources.')
param tags resourceInput<'Microsoft.Resources/resourceGroups@2025-04-01'>.tags = {}

@description('Optional. Enable monitoring for applicable resources.')
param enableMonitoring bool = false

@description('Optional. Enable scalability for applicable resources.')
param enableScalability bool = false

@description('Optional. Enable redundancy for applicable resources.')
param enableRedundancy bool = false

@description('Optional. Enable private networking for applicable resources.')
param enablePrivateNetworking bool = false

@description('Optional. The Container Registry hostname.')
param acrName string = 'contentgencontainerreg'

@description('Optional. Image Tag.')
param imageTag string = 'latest'

@description('Optional. Enable/Disable usage telemetry.')
param enableTelemetry bool = true

@description('Optional. Enable purge protection for Key Vault.')
param enablePurgeProtection bool = false

@description('Optional. Created by user name.')
param createdBy string = contains(deployer(), 'userPrincipalName')? split(deployer().userPrincipalName, '@')[0]: deployer().objectId

// ============== //
// Variables      //
// ============== //

var solutionLocation = empty(location) ? resourceGroup().location : location
var solutionSuffix = toLower(trim(replace(
  replace(
    replace(replace(replace(replace('${solutionName}${solutionUniqueText}', '-', ''), '_', ''), '.', ''), '/', ''),
    ' ',
    ''
  ),
  '*',
  ''
)))

var cosmosDbZoneRedundantHaRegionPairs = {
  australiaeast: 'uksouth'
  centralus: 'eastus2'
  eastasia: 'southeastasia'
  eastus: 'centralus'
  eastus2: 'centralus'
  japaneast: 'australiaeast'
  northeurope: 'westeurope'
  southeastasia: 'eastasia'
  uksouth: 'westeurope'
}
var cosmosDbHaLocation = cosmosDbZoneRedundantHaRegionPairs[resourceGroup().location]

var replicaRegionPairs = {
  australiaeast: 'australiasoutheast'
  centralus: 'westus'
  eastasia: 'japaneast'
  eastus: 'centralus'
  eastus2: 'centralus'
  japaneast: 'eastasia'
  northeurope: 'westeurope'
  southeastasia: 'eastasia'
  uksouth: 'westeurope'
}
var replicaLocation = replicaRegionPairs[resourceGroup().location]

var appEnvironment = 'Prod'
var azureCosmosDbEnableFeedback = 'True'

// Extracts subscription, resource group, and workspace name from the resource ID
var useExistingLogAnalytics = !empty(existingLogAnalyticsWorkspaceId)
var useExistingAiFoundryAiProject = !empty(azureExistingAIProjectResourceId)
var aiFoundryAiServicesResourceGroupName = useExistingAiFoundryAiProject
  ? split(azureExistingAIProjectResourceId, '/')[4]
  : 'rg-${solutionSuffix}'
var aiFoundryAiServicesSubscriptionId = useExistingAiFoundryAiProject
  ? split(azureExistingAIProjectResourceId, '/')[2]
  : subscription().id
var aiFoundryAiServicesResourceName = useExistingAiFoundryAiProject
  ? split(azureExistingAIProjectResourceId, '/')[8]
  : 'aif-${solutionSuffix}'
var aiFoundryAiProjectResourceName = useExistingAiFoundryAiProject
  ? split(azureExistingAIProjectResourceId, '/')[10]
  : 'proj-${solutionSuffix}'
var aiFoundryAiServicesModelDeployment = [
  {
    format: 'OpenAI'
    name: gptModelName
    model: gptModelName
    sku: {
      name: gptModelDeploymentType
      capacity: gptModelCapacity
    }
    version: gptModelVersion
    raiPolicyName: 'Microsoft.Default'
  }
  {
    format: 'OpenAI'
    name: dalleModelName
    model: dalleModelName
    sku: {
      name: 'Standard'
      capacity: dalleModelCapacity
    }
    version: dalleModelVersion
    raiPolicyName: 'Microsoft.Default'
  }
  {
    format: 'OpenAI'
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
var aiFoundryAiProjectDescription = 'Content Generation AI Foundry Project'

// ============== //
// Resources      //
// ============== //

#disable-next-line no-deployments-resources
resource avmTelemetry 'Microsoft.Resources/deployments@2024-03-01' = if (enableTelemetry) {
  name: '46d3xbcp.ptn.sa-contentgen.${replace('-..--..-', '.', '-')}.${substring(uniqueString(deployment().name, solutionLocation), 0, 4)}'
  properties: {
    mode: 'Incremental'
    template: {
      '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
      contentVersion: '1.0.0.0'
      resources: []
      outputs: {
        telemetry: {
          type: 'String'
          value: 'For more information, see https://aka.ms/avm/TelemetryInfo'
        }
      }
    }
  }
}

// ========== Resource Group Tag ========== //
resource resourceGroupTags 'Microsoft.Resources/tags@2021-04-01' = {
  name: 'default'
  properties: {
    tags: {
      ...resourceGroup().tags
      ... tags
      TemplateName: 'ContentGen'
      Type: enablePrivateNetworking ? 'WAF' : 'Non-WAF'
      CreatedBy: createdBy
    }
  }
}

// ========== Log Analytics Workspace ========== //
var logAnalyticsWorkspaceResourceName = 'log-${solutionSuffix}'
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.12.0' = if (enableMonitoring && !useExistingLogAnalytics) {
  name: take('avm.res.operational-insights.workspace.${logAnalyticsWorkspaceResourceName}', 64)
  params: {
    name: logAnalyticsWorkspaceResourceName
    tags: tags
    location: solutionLocation
    enableTelemetry: enableTelemetry
    skuName: 'PerGB2018'
    dataRetention: 365
    features: { enableLogAccessUsingOnlyResourcePermissions: true }
    diagnosticSettings: [{ useThisWorkspace: true }]
    dailyQuotaGb: enableRedundancy ? 10 : null
    replication: enableRedundancy
      ? {
          enabled: true
          location: replicaLocation
        }
      : null
    publicNetworkAccessForIngestion: enablePrivateNetworking ? 'Disabled' : 'Enabled'
    publicNetworkAccessForQuery: enablePrivateNetworking ? 'Disabled' : 'Enabled'
  }
}
var logAnalyticsWorkspaceResourceId = useExistingLogAnalytics ? existingLogAnalyticsWorkspaceId : logAnalyticsWorkspace!.outputs.resourceId

// ========== Application Insights ========== //
var applicationInsightsResourceName = 'appi-${solutionSuffix}'
module applicationInsights 'br/public:avm/res/insights/component:0.6.0' = if (enableMonitoring) {
  name: take('avm.res.insights.component.${applicationInsightsResourceName}', 64)
  params: {
    name: applicationInsightsResourceName
    tags: tags
    location: solutionLocation
    enableTelemetry: enableTelemetry
    retentionInDays: 365
    kind: 'web'
    disableIpMasking: false
    flowType: 'Bluefield'
    workspaceResourceId: logAnalyticsWorkspaceResourceId
    diagnosticSettings: [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }]
  }
}

// ========== User Assigned Identity ========== //
var userAssignedIdentityResourceName = 'id-${solutionSuffix}'
module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.1' = {
  name: take('avm.res.managed-identity.user-assigned-identity.${userAssignedIdentityResourceName}', 64)
  params: {
    name: userAssignedIdentityResourceName
    location: solutionLocation
    tags: tags
    enableTelemetry: enableTelemetry
  }
}

// ========== AI Foundry: AI Services ========== //
module aiFoundryAiServices 'br:mcr.microsoft.com/bicep/avm/res/cognitive-services/account:0.13.2' = if (!useExistingAiFoundryAiProject) {
  name: take('avm.res.cognitive-services.account.${aiFoundryAiServicesResourceName}', 64)
  params: {
    name: aiFoundryAiServicesResourceName
    location: azureAiServiceLocation 
    tags: tags
    sku: 'S0'
    kind: 'AIServices'
    disableLocalAuth: true
    allowProjectManagement: true
    customSubDomainName: aiFoundryAiServicesResourceName
    restrictOutboundNetworkAccess: false
    deployments: [
      for deployment in aiFoundryAiServicesModelDeployment: {
        name: deployment.name
        model: {
          format: deployment.format
          name: deployment.name
          version: deployment.version
        }
        raiPolicyName: deployment.raiPolicyName
        sku: {
          name: deployment.sku.name
          capacity: deployment.sku.capacity
        }
      }
    ]
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    managedIdentities: { 
      userAssignedResourceIds: [userAssignedIdentity!.outputs.resourceId] 
    }
    roleAssignments: [
      {
        roleDefinitionIdOrName: '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Azure AI User
        principalId: userAssignedIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
      }
      {
        roleDefinitionIdOrName: '64702f94-c441-49e6-a78b-ef80e0188fee' // Azure AI Developer
        principalId: userAssignedIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
      }
      {
        roleDefinitionIdOrName: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
        principalId: userAssignedIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
      }
    ]
    diagnosticSettings: enableMonitoring ? [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }] : null
    publicNetworkAccess: enablePrivateNetworking ? 'Disabled' : 'Enabled'
  }
}

module aiFoundryAiServicesProject 'modules/ai-project.bicep' = if (!useExistingAiFoundryAiProject) {
  name: take('module.ai-project.${aiFoundryAiProjectResourceName}', 64)
  params: {
    name: aiFoundryAiProjectResourceName
    location: azureAiServiceLocation 
    tags: tags
    desc: aiFoundryAiProjectDescription
    aiServicesName: aiFoundryAiServicesResourceName
    azureExistingAIProjectResourceId: azureExistingAIProjectResourceId
  }
  dependsOn: [
    aiFoundryAiServices
  ]
}

var aiFoundryAiProjectEndpoint = useExistingAiFoundryAiProject
  ? 'https://${aiFoundryAiServicesResourceName}.services.ai.azure.com/api/projects/${aiFoundryAiProjectResourceName}'
  : aiFoundryAiServicesProject!.outputs.apiEndpoint

// ========== Storage Account ========== //
var storageAccountName = 'st${solutionSuffix}'
var productImagesContainer = 'product-images'
var generatedImagesContainer = 'generated-images'

module storageAccount 'br/public:avm/res/storage/storage-account:0.20.0' = {
  name: take('avm.res.storage.storage-account.${storageAccountName}', 64)
  params: {
    name: storageAccountName
    location: solutionLocation
    skuName: 'Standard_LRS'
    managedIdentities: { systemAssigned: true }
    minimumTlsVersion: 'TLS1_2'
    enableTelemetry: enableTelemetry
    tags: tags
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    blobServices: {
      containerDeleteRetentionPolicyEnabled: false
      containerDeleteRetentionPolicyDays: 7
      deleteRetentionPolicyEnabled: false
      deleteRetentionPolicyDays: 6
      containers: [
        {
          name: productImagesContainer
          publicAccess: 'None'
          denyEncryptionScopeOverride: false
          defaultEncryptionScope: '$account-encryption-key'
        }
        {
          name: generatedImagesContainer
          publicAccess: 'None'
          denyEncryptionScopeOverride: false
          defaultEncryptionScope: '$account-encryption-key'
        }
      ]
    }
    roleAssignments: [
      {
        principalId: userAssignedIdentity.outputs.principalId
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalType: 'ServicePrincipal'
      }
    ]
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: enablePrivateNetworking ? 'Deny' : 'Allow'
    }
    allowBlobPublicAccess: enablePrivateNetworking ? true : false
    publicNetworkAccess: enablePrivateNetworking ? 'Disabled' : 'Enabled'
  }
}

// ========== Cosmos DB ========== //
var cosmosDBResourceName = 'cosmos-${solutionSuffix}'
var cosmosDBDatabaseName = 'content_generation_db'
var cosmosDBConversationsContainer = 'conversations'
var cosmosDBProductsContainer = 'products'

module cosmosDB 'br/public:avm/res/document-db/database-account:0.15.0' = {
  name: take('avm.res.document-db.database-account.${cosmosDBResourceName}', 64)
  params: {
    name: 'cosmos-${solutionSuffix}'
    location: secondaryLocation
    tags: tags
    enableTelemetry: enableTelemetry
    sqlDatabases: [
      {
        name: cosmosDBDatabaseName
        containers: [
          {
            name: cosmosDBConversationsContainer
            paths: [
              '/userId'
            ]
          }
          {
            name: cosmosDBProductsContainer
            paths: [
              '/category'
            ]
          }
        ]
      }
    ]
    dataPlaneRoleDefinitions: [
      {
        roleName: 'Cosmos DB SQL Data Contributor'
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*'
        ]
        assignments: [{ principalId: userAssignedIdentity.outputs.principalId }]
      }
    ]
    diagnosticSettings: enableMonitoring ? [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }] : null
    networkRestrictions: {
      networkAclBypass: 'None'
      publicNetworkAccess: enablePrivateNetworking ? 'Disabled' : 'Enabled'
    }
    zoneRedundant: enableRedundancy ? true : false
    capabilitiesToAdd: enableRedundancy ? null : ['EnableServerless']
    automaticFailover: enableRedundancy ? true : false
    failoverLocations: enableRedundancy
      ? [
          {
            failoverPriority: 0
            isZoneRedundant: true
            locationName: secondaryLocation
          }
          {
            failoverPriority: 1
            isZoneRedundant: true
            locationName: cosmosDbHaLocation
          }
        ]
      : [
          {
            locationName: secondaryLocation
            failoverPriority: 0
            isZoneRedundant: enableRedundancy
          }
        ]
  }
}

// ========== Key Vault ========== //
var keyVaultName = 'kv-${solutionSuffix}'
module keyvault 'br/public:avm/res/key-vault/vault:0.12.1' = {
  name: take('avm.res.key-vault.vault.${keyVaultName}', 64)
  params: {
    name: keyVaultName
    location: solutionLocation
    tags: tags
    sku: 'standard'
    publicNetworkAccess: enablePrivateNetworking ? 'Disabled' : 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    enableVaultForDeployment: true
    enableVaultForDiskEncryption: true
    enableVaultForTemplateDeployment: true
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: enablePurgeProtection
    softDeleteRetentionInDays: 7
    diagnosticSettings: enableMonitoring 
      ? [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }] 
      : []
    roleAssignments: [
      {
         principalId: userAssignedIdentity.outputs.principalId
         principalType: 'ServicePrincipal'
         roleDefinitionIdOrName: 'Key Vault Administrator'
      }
    ]
    enableTelemetry: enableTelemetry
    secrets: [
      {
        name: 'STORAGE-ACCOUNT-NAME'
        value: storageAccountName
      }
      {
        name: 'STORAGE-ACCOUNT-KEY'
        value: storageAccount.outputs.primaryAccessKey
      }
      {
        name: 'AZURE-COSMOSDB-ACCOUNT'
        value: cosmosDB.outputs.name
      }
      {
        name: 'AZURE-COSMOSDB-ACCOUNT-KEY'
        value: cosmosDB.outputs.primaryReadWriteKey
      }
      {
        name: 'AZURE-COSMOSDB-DATABASE'
        value: cosmosDBDatabaseName
      }
      {
        name: 'AZURE-COSMOSDB-CONVERSATIONS-CONTAINER'
        value: cosmosDBConversationsContainer
      }
      {
        name: 'AZURE-COSMOSDB-PRODUCTS-CONTAINER'
        value: cosmosDBProductsContainer
      }
      {name: 'AZURE-LOCATION', value: azureAiServiceLocation }
      {name: 'AZURE-RESOURCE-GROUP', value: resourceGroup().name}
      {name: 'AZURE-SUBSCRIPTION-ID', value: subscription().subscriptionId}
      {
        name: 'COG-SERVICES-NAME'
        value: aiFoundryAiServicesResourceName
      }
      {
        name: 'COG-SERVICES-ENDPOINT'
        value: 'https://${aiFoundryAiServicesResourceName}.openai.azure.com/'
      }
      {name: 'AZURE-OPENAI-MODEL', value: gptModelName}
      {name: 'AZURE-DALLE-MODEL', value: dalleModelName}
      {name: 'AZURE-OPENAI-EMBEDDING-MODEL', value: embeddingModel}
      {
        name: 'AZURE-OPENAI-ENDPOINT'
        value: 'https://${aiFoundryAiServicesResourceName}.openai.azure.com/'
      }
      {name: 'AZURE-OPENAI-PREVIEW-API-VERSION', value: azureOpenaiAPIVersion}
      {name: 'TENANT-ID', value: subscription().tenantId}
    ]
  }
}

// ========== App Service Plan ========== //
var webServerFarmResourceName = 'asp-${solutionSuffix}'
module webServerFarm 'br/public:avm/res/web/serverfarm:0.5.0' = {
  name: take('avm.res.web.serverfarm.${webServerFarmResourceName}', 64)
  params: {
    name: webServerFarmResourceName
    tags: tags
    enableTelemetry: enableTelemetry
    location: solutionLocation
    reserved: true
    kind: 'linux'
    diagnosticSettings: enableMonitoring ? [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }] : null
    skuName: enableScalability || enableRedundancy ? 'P1v3' : 'B3'
    skuCapacity: 1
    zoneRedundant: enableRedundancy ? true : false
  }
  scope: resourceGroup(resourceGroup().name)
}

// ========== Web App ========== //
var webSiteResourceName = 'app-${solutionSuffix}'
module webSite 'modules/web-sites.bicep' = {
  name: take('module.web-sites.${webSiteResourceName}', 64)
  params: {
    name: webSiteResourceName
    tags: tags
    location: solutionLocation
    kind: 'app,linux,container'
    serverFarmResourceId: webServerFarm.outputs.resourceId
    managedIdentities: { userAssignedResourceIds: [userAssignedIdentity!.outputs.resourceId] }
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acrName}.azurecr.io/webapp:${imageTag}'
      minTlsVersion: '1.2'
    }
    configs: concat([
      {
        name: 'appsettings'
        properties: {
          SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
          DOCKER_REGISTRY_SERVER_URL: 'https://${acrName}.azurecr.io'
          AUTH_ENABLED: 'false'
          // Azure OpenAI Settings
          AZURE_OPENAI_API_VERSION: azureOpenaiAPIVersion
          AZURE_OPENAI_MODEL: gptModelName
          AZURE_DALLE_MODEL: dalleModelName
          AZURE_OPENAI_ENDPOINT: 'https://${aiFoundryAiServicesResourceName}.openai.azure.com/'
          AZURE_OPENAI_RESOURCE: aiFoundryAiServicesResourceName
          AZURE_OPENAI_PREVIEW_API_VERSION: azureOpenaiAPIVersion
          // AI Agent Settings
          AZURE_AI_AGENT_ENDPOINT: aiFoundryAiProjectEndpoint
          AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME: gptModelName
          AZURE_AI_AGENT_API_VERSION: azureAiAgentApiVersion
          // Storage Settings
          AZURE_STORAGE_ACCOUNT: storageAccountName
          AZURE_STORAGE_PRODUCT_IMAGES_CONTAINER: productImagesContainer
          AZURE_STORAGE_GENERATED_IMAGES_CONTAINER: generatedImagesContainer
          // CosmosDB Settings
          SOLUTION_NAME: solutionName
          USE_CHAT_HISTORY_ENABLED: 'True'
          AZURE_COSMOSDB_ACCOUNT: cosmosDB.outputs.name
          AZURE_COSMOSDB_ACCOUNT_KEY: ''
          AZURE_COSMOSDB_CONVERSATIONS_CONTAINER: cosmosDBConversationsContainer
          AZURE_COSMOSDB_PRODUCTS_CONTAINER: cosmosDBProductsContainer
          AZURE_COSMOSDB_DATABASE: cosmosDBDatabaseName
          AZURE_COSMOSDB_ENABLE_FEEDBACK: azureCosmosDbEnableFeedback
          // Brand Guidelines (configured via environment)
          BRAND_TONE: 'Professional yet approachable'
          BRAND_VOICE: 'Innovative, trustworthy, customer-focused'
          BRAND_PROHIBITED_WORDS: 'guarantee,best,only,exclusive,cheapest'
          BRAND_REQUIRED_DISCLOSURES: 'Terms apply,See details for eligibility'
          BRAND_PRIMARY_COLOR: '#0078D4'
          BRAND_SECONDARY_COLOR: '#107C10'
          BRAND_IMAGE_STYLE: 'Modern, clean, minimalist with bright lighting'
          BRAND_TYPOGRAPHY: 'Sans-serif, bold headlines, readable body text'
          // App Settings
          UWSGI_PROCESSES: '2'
          UWSGI_THREADS: '2'
          APP_ENV: appEnvironment
          AZURE_CLIENT_ID: userAssignedIdentity.outputs.clientId
        }
        applicationInsightResourceId: enableMonitoring ? applicationInsights!.outputs.resourceId : null
      }
    ], enableMonitoring ? [
      {
        name: 'logs'
        properties: {}
      }
    ] : [])
    enableMonitoring: enableMonitoring
    diagnosticSettings: enableMonitoring ? [{ workspaceResourceId: logAnalyticsWorkspaceResourceId }] : null
    vnetRouteAllEnabled: enablePrivateNetworking ? true : false
    vnetImagePullEnabled: enablePrivateNetworking ? true : false
    publicNetworkAccess: 'Enabled'
  }
}

// ========== Outputs ========== //
@description('Contains WebApp URL')
output WEB_APP_URL string = 'https://${webSite.outputs.name}.azurewebsites.net'

@description('Contains Storage Account Name')
output STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name

@description('Contains Product Images Container')
output STORAGE_PRODUCT_IMAGES_CONTAINER string = productImagesContainer

@description('Contains Generated Images Container')
output STORAGE_GENERATED_IMAGES_CONTAINER string = generatedImagesContainer

@description('Contains KeyVault Name')
output KEY_VAULT_NAME string = keyvault.outputs.name

@description('Contains CosmosDB Account Name')
output COSMOSDB_ACCOUNT_NAME string = cosmosDB.outputs.name

@description('Contains CosmosDB Database Name')
output COSMOSDB_DATABASE_NAME string = cosmosDBDatabaseName

@description('Contains CosmosDB Products Container')
output COSMOSDB_PRODUCTS_CONTAINER string = cosmosDBProductsContainer

@description('Contains CosmosDB Conversations Container')
output COSMOSDB_CONVERSATIONS_CONTAINER string = cosmosDBConversationsContainer

@description('Contains Resource Group Name')
output RESOURCE_GROUP_NAME string = resourceGroup().name

@description('Contains AI Foundry Name')
output AI_FOUNDRY_NAME string = aiFoundryAiProjectResourceName

@description('Contains AI Foundry RG Name')
output AI_FOUNDRY_RG_NAME string = aiFoundryAiServicesResourceGroupName

@description('Contains AI Foundry Resource ID')
output AI_FOUNDRY_RESOURCE_ID string = useExistingAiFoundryAiProject ? '' : aiFoundryAiServices!.outputs.resourceId

@description('Contains GPT Model')
output AZURE_OPENAI_MODEL string = gptModelName

@description('Contains DALL-E Model')
output AZURE_DALLE_MODEL string = dalleModelName

@description('Contains OpenAI Resource')
output AZURE_OPENAI_RESOURCE string = aiFoundryAiServicesResourceName

@description('Contains AI Agent Endpoint')
output AZURE_AI_AGENT_ENDPOINT string = aiFoundryAiProjectEndpoint

@description('Contains AI Agent API Version')
output AZURE_AI_AGENT_API_VERSION string = azureAiAgentApiVersion

@description('Contains Application Insights Connection String')
output AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING string = (enableMonitoring && !useExistingLogAnalytics) ? applicationInsights!.outputs.connectionString : ''

@description('Contains Application Environment')
output APP_ENV string = appEnvironment
