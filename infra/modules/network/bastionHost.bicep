// /****************************************************************************************************************************/
// Create Azure Bastion Host
// /****************************************************************************************************************************/

@description('Name of the Azure Bastion Host resource.')
param name string

@description('Azure region to deploy resources.')
param location string = resourceGroup().location

@description('Resource ID of the Virtual Network where the Azure Bastion Host will be deployed.')
param vnetId string

@description('Resource ID of the Log Analytics Workspace for monitoring and diagnostics.')
param logAnalyticsWorkspaceId string

@description('Optional. Tags to apply to the resources.')
param tags object = {}

@description('Optional. Enable/Disable usage telemetry for module.')
param enableTelemetry bool = true

// Create Azure Bastion Host using AVM Bastion Host module
// https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/network/bastion-host
module bastionHost 'br/public:avm/res/network/bastion-host:0.6.1' = {
  name: take('avm.res.network.bastion-host.${name}', 64)
  params: {
    name: name
    skuName: 'Standard'
    location: location
    virtualNetworkResourceId: vnetId
    diagnosticSettings: [
      {
        name: 'bastionDiagnostics'
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
      }
    ]
    tags: tags
    enableTelemetry: enableTelemetry
    publicIPAddressObject: {
      name: 'pip-${name}'
      zones: []
    }
  }
}

output resourceId string = bastionHost.outputs.resourceId
output name string = bastionHost.outputs.name
