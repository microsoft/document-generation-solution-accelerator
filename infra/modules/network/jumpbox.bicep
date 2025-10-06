// /****************************************************************************************************************************/
// Create Jumpbox VM - Simplified with minimal parameters
// /****************************************************************************************************************************/

@description('Name of the Jumpbox Virtual Machine.')
param name string

@description('Azure region to deploy resources.')
param location string = resourceGroup().location

@description('Size of the Jumpbox Virtual Machine.')
param size string

@description('Resource ID of the jumpbox subnet.')
param subnetResourceId string

@description('Username to access the Jumpbox VM.')
param username string

@secure()
@description('Password to access the Jumpbox VM.')
param password string 

@description('Optional. Tags to apply to the resources.')
param tags object = {}

@description('Log Analytics Workspace Resource ID for VM diagnostics.')
param logAnalyticsWorkspaceId string

@description('Optional. Enable/Disable usage telemetry for module.')
param enableTelemetry bool = true

// Create Jumpbox VM using AVM Virtual Machine module 
// https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/compute/virtual-machine
var vmName = take(name, 15) // Shorten VM name to 15 characters to avoid Azure limits

module vm 'br/public:avm/res/compute/virtual-machine:0.15.0' = {
  name: take('avm.res.compute.virtual-machine.${vmName}', 64)
  params: {
    name: vmName
    vmSize: size
    location: location
    adminUsername: username
    adminPassword: password
    tags: tags
    zone: 0
    imageReference: {
      offer: 'WindowsServer'
      publisher: 'MicrosoftWindowsServer'
      sku: '2019-datacenter'
      version: 'latest'
    }
    osType: 'Windows'
    osDisk: {
      name: 'osdisk-${vmName}'
      managedDisk: {
        storageAccountType: 'Standard_LRS'
      }
    }
    encryptionAtHost: false // Some Azure subscriptions do not support encryption at host
    nicConfigurations: [
      {
        name: 'nic-${vmName}'
        ipConfigurations: [
          {
            name: 'ipconfig1'
            subnetResourceId: subnetResourceId
          }
        ]
        diagnosticSettings: [
          {
            name: 'jumpboxDiagnostics'
            workspaceResourceId: logAnalyticsWorkspaceId
            logCategoriesAndGroups: [
              {
                categoryGroup: 'allLogs'
                enabled: true
              }
            ]
            metricCategories: [
              {
                category: 'AllMetrics'
                enabled: true
              }
            ]
          }
        ]
      }
    ]
    enableTelemetry: enableTelemetry
  }
}

output resourceId string = vm.outputs.resourceId
output name string = vm.outputs.name
output location string = vm.outputs.location
