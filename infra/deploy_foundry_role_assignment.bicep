@description('Principle ID')
param principalId string = ''

@description('Role Definition ID')
param roleDefinitionId string

@description('Role Assignment Name')
param roleAssignmentName string = ''

@description('AI Foundry Name')
param aiFoundryName string

@description('AI Project Name')
param aiProjectName string = ''

@description('AI Model Deployments')
param aiModelDeployments array = []

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: aiFoundryName
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = if (!empty(aiProjectName)) {
  name: aiProjectName
  parent: aiServices
}

@batchSize(1)
resource aiServicesDeployments 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = [for aiModeldeployment in aiModelDeployments: if (!empty(aiModelDeployments)) {
  parent: aiServices
  name: aiModeldeployment.name
  properties: {
    model: {
      format: 'OpenAI'
      name: aiModeldeployment.model
    }
    raiPolicyName: aiModeldeployment.raiPolicyName
  }
  sku:{
    name: aiModeldeployment.sku.name
    capacity: aiModeldeployment.sku.capacity
  }
  tags : tags
}]


resource roleAssignmentToFoundry 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: roleAssignmentName
  scope: aiServices
  properties: {
    roleDefinitionId: roleDefinitionId
    principalId: principalId
  }
}

@description('AI Service Principle ID')
output aiServicesPrincipalId string = aiServices.identity.principalId

@description('AI Project Principle ID')
output aiProjectPrincipalId string = !empty(aiProjectName) ? aiProject.identity.principalId : ''
