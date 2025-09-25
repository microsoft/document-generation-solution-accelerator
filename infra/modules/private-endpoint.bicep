// ========== Private Endpoint Module ========== //
@description('Name of the private endpoint')
param name string

@description('Location for the private endpoint')
param location string = resourceGroup().location

@description('Subnet resource ID where the private endpoint will be created')
param subnetResourceId string

@description('Resource ID of the target resource for the private endpoint')
param targetResourceId string

@description('Group IDs for the private endpoint connection')
param groupIds array = ['account']

@description('Custom network interface name for the private endpoint')
param customNetworkInterfaceName string = ''

@description('Private DNS zone group configurations')
param privateDnsZoneGroupConfigs array = []

@description('Tags to apply to the private endpoint')
param tags object = {}

// ========== Private Endpoint Resource ========== //
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetResourceId
    }
    privateLinkServiceConnections: [
      {
        name: name
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds: groupIds
        }
      }
    ]
    customNetworkInterfaceName: !empty(customNetworkInterfaceName) ? customNetworkInterfaceName : null
  }
}

// ========== Private DNS Zone Group ========== //
resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = if (!empty(privateDnsZoneGroupConfigs)) {
  name: 'default'
  parent: privateEndpoint
  properties: {
    privateDnsZoneConfigs: [
      for config in privateDnsZoneGroupConfigs: {
        name: config.name
        properties: {
          privateDnsZoneId: config.privateDnsZoneResourceId
        }
      }
    ]
  }
}

// ========== Outputs ========== //
@description('Resource ID of the private endpoint')
output resourceId string = privateEndpoint.id

@description('Name of the private endpoint')
output name string = privateEndpoint.name

@description('Location of the private endpoint')
output location string = privateEndpoint.location

@description('Network interface resource IDs associated with the private endpoint')
output networkInterfaceResourceIds array = privateEndpoint.properties.networkInterfaces
