// /****************************************************************************************************************************/
// Virtual Network with NSGs and Subnets - All networking components in one module
// /****************************************************************************************************************************/

@description('Name of the virtual network.')
param name string 

@description('Azure region to deploy resources.')
param location string = resourceGroup().location

@description('Required. An Array of 1 or more IP Address Prefixes for the Virtual Network.')
param addressPrefixes array

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

@description('Optional. The resource ID of the Log Analytics Workspace to send diagnostic logs to.')
param logAnalyticsWorkspaceId string

@description('Optional. Enable/Disable usage telemetry for module.')
param enableTelemetry bool = true

@description('Required. Suffix for resource naming.')
param resourceSuffix string

// Create NSGs for each subnet type
module nsgWeb 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: take('avm.res.network.network-security-group.web.${resourceSuffix}', 64)
  params: {
    name: 'nsg-${resourceSuffix}-web'
    location: location
    tags: tags
    enableTelemetry: enableTelemetry
    securityRules: [
      {
        name: 'AllowHttpsInbound'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 100
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefixes: ['0.0.0.0/0']
          destinationAddressPrefixes: ['10.0.0.0/23']
        }
      }
      {
        name: 'AllowIntraSubnetTraffic'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 200
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefixes: ['10.0.0.0/23']
          destinationAddressPrefixes: ['10.0.0.0/23']
        }
      }
      {
        name: 'AllowAzureLoadBalancer'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 300
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: 'AzureLoadBalancer'
          destinationAddressPrefix: '10.0.0.0/23'
        }
      }
    ]
  }
}

module nsgPeps 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: take('avm.res.network.network-security-group.peps.${resourceSuffix}', 64)
  params: {
    name: 'nsg-${resourceSuffix}-peps'
    location: location
    tags: tags
    enableTelemetry: enableTelemetry
    securityRules: []
  }
}

module nsgBastion 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: take('avm.res.network.network-security-group.bastion.${resourceSuffix}', 64)
  params: {
    name: 'nsg-${resourceSuffix}-bastion'
    location: location
    tags: tags
    enableTelemetry: enableTelemetry
    securityRules: [
      {
        name: 'AllowGatewayManager'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 2702
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'GatewayManager'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'AllowHttpsInBound'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 2703
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'AllowSshRdpOutbound'
        properties: {
          access: 'Allow'
          direction: 'Outbound'
          priority: 100
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRanges: ['22', '3389']
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'VirtualNetwork'
        }
      }
      {
        name: 'AllowAzureCloudOutbound'
        properties: {
          access: 'Allow'
          direction: 'Outbound'
          priority: 110
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'AzureCloud'
        }
      }
    ]
  }
}

module nsgJumpbox 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: take('avm.res.network.network-security-group.jumpbox.${resourceSuffix}', 64)
  params: {
    name: 'nsg-${resourceSuffix}-jumpbox'
    location: location
    tags: tags
    enableTelemetry: enableTelemetry
    securityRules: [
      {
        name: 'AllowRdpFromBastion'
        properties: {
          access: 'Allow'
          direction: 'Inbound'
          priority: 100
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '3389'
          sourceAddressPrefixes: ['10.0.10.0/26'] // Azure Bastion subnet
          destinationAddressPrefixes: ['10.0.12.0/23']
        }
      }
    ]
  }
}

// Create Virtual Network with all subnets
module virtualNetwork 'br/public:avm/res/network/virtual-network:0.7.0' = {
  name: take('avm.res.network.virtual-network.${name}', 64)
  params: {
    name: name
    location: location
    addressPrefixes: addressPrefixes
    subnets: [
      {
        name: 'web'
        addressPrefixes: ['10.0.0.0/23'] // /23 (10.0.0.0 - 10.0.1.255), 512 addresses
        networkSecurityGroupResourceId: nsgWeb.outputs.resourceId
        delegation: 'Microsoft.Web/serverFarms'
      }
      {
        name: 'peps'
        addressPrefixes: ['10.0.2.0/23'] // /23 (10.0.2.0 - 10.0.3.255), 512 addresses
        privateEndpointNetworkPolicies: 'Disabled'
        privateLinkServiceNetworkPolicies: 'Disabled'
        networkSecurityGroupResourceId: nsgPeps.outputs.resourceId
      }
      {
        name: 'AzureBastionSubnet' // Required name for Azure Bastion
        addressPrefixes: ['10.0.10.0/26']
        networkSecurityGroupResourceId: nsgBastion.outputs.resourceId
      }
      {
        name: 'jumpbox'
        addressPrefixes: ['10.0.12.0/23'] // /23 (10.0.12.0 - 10.0.13.255), 512 addresses
        networkSecurityGroupResourceId: nsgJumpbox.outputs.resourceId
      }
    ]
    diagnosticSettings: [
      {
        name: 'vnetDiagnostics'
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
    tags: tags
    enableTelemetry: enableTelemetry
  }
}

// Outputs
output name string = virtualNetwork.outputs.name
output resourceId string = virtualNetwork.outputs.resourceId
output webSubnetResourceId string = '${virtualNetwork.outputs.resourceId}/subnets/web'
output pepsSubnetResourceId string = '${virtualNetwork.outputs.resourceId}/subnets/peps'
output bastionSubnetResourceId string = '${virtualNetwork.outputs.resourceId}/subnets/AzureBastionSubnet'
output jumpboxSubnetResourceId string = '${virtualNetwork.outputs.resourceId}/subnets/jumpbox'

// NSG Resource IDs for potential external references
output webNsgResourceId string = nsgWeb.outputs.resourceId
output pepsNsgResourceId string = nsgPeps.outputs.resourceId
output bastionNsgResourceId string = nsgBastion.outputs.resourceId
output jumpboxNsgResourceId string = nsgJumpbox.outputs.resourceId

// Export types for use in other modules
@export()
@description('Custom type definition for bastion host configuration.')
type bastionHostConfigurationType = {
  @description('The name of the Bastion Host resource.')
  name: string
}

@export()
@description('Custom type definition for jumpbox VM configuration.')
type jumpBoxConfigurationType = {
  @description('The name of the Virtual Machine.')
  name: string

  @description('The size of the VM.')
  size: string?

  @description('Username to access VM.')
  username: string

  @secure()
  @description('Password to access VM.')
  password: string
}
