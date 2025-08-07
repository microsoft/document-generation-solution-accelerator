@description('Specifies the location for resources.')
param solutionLocation string

@description('Contains BaseURL.')
param baseUrl string

@description('Contains Managed Identity Object ID.')
param managedIdentityObjectId string

@description('Contains Storage Account Name.')
param storageAccountName string

@description('Contains Container Name.')
param containerName string

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

resource copy_demo_Data 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  kind:'AzureCLI'
  name: 'copy_demo_Data'
  location: solutionLocation // Replace with your desired location
  identity:{
    type:'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityObjectId}' : {}
    }
  }
  properties: {
    azCliVersion: '2.50.0'
    primaryScriptUri: '${baseUrl}infra/scripts/copy_kb_files.sh' // deploy-azure-synapse-pipelines.sh
    arguments: '${storageAccountName} ${containerName} ${baseUrl}' // Specify any arguments for the script
    timeout: 'PT1H' // Specify the desired timeout duration
    retentionInterval: 'PT1H' // Specify the desired retention interval
    cleanupPreference:'OnSuccess'
  }
  tags : tags
}
