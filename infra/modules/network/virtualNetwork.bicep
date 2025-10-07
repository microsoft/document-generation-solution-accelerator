/****************************************************************************************************************************/
// Networking - NSGs, VNET and Subnets. Each subnet has its own NSG
/****************************************************************************************************************************/
@description('Name of the virtual network.')
param name string 

@description('Azure region to deploy resources.')
param location string = resourceGroup().location

@description('Required. An Array of 1 or more IP Address Prefixes for the Virtual Network.')
param addressPrefixes array

@description('An array of subnets to be created within the virtual network. Each subnet can have its own configuration and associated Network Security Group (NSG).')
param subnets subnetType[] = [
  {
    name: 'web'
    addressPrefixes: ['10.0.0.0/23'] // /23 (10.0.0.0 - 10.0.1.255), 512 addresses
    delegation: 'Microsoft.Web/serverFarms'
    networkSecurityGroup: {
      name: 'web'
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
  {
    name: 'peps'
    addressPrefixes: ['10.0.2.0/23'] // /23 (10.0.2.0 - 10.0.3.255), 512 addresses
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
    networkSecurityGroup: {
      name: 'peps'
      securityRules: []
    }
  }
  {
    name: 'AzureBastionSubnet' // Required name for Azure Bastion
    addressPrefixes: ['10.0.10.0/26']
    networkSecurityGroup: {
      name: 'bastion'
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
  {
    name: 'jumpbox'
    addressPrefixes: ['10.0.12.0/23'] // /23 (10.0.12.0 - 10.0.13.255), 512 addresses
    networkSecurityGroup: {
      name: 'jumpbox'
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
]

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

@description('Optional. The resource ID of the Log Analytics Workspace to send diagnostic logs to.')
param logAnalyticsWorkspaceId string

@description('Optional. Enable/Disable usage telemetry for module.')
param enableTelemetry bool = true

@description('Required. Suffix for resource naming.')
param resourceSuffix string

// 1. Create NSGs for subnets 
// using AVM Network Security Group module
// https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/network/network-security-group

@batchSize(1)
module nsgs 'br/public:avm/res/network/network-security-group:0.5.1' = [
  for (subnet, i) in subnets: if (!empty(subnet.?networkSecurityGroup)) {
    name: take('avm.res.network.network-security-group.${subnet.?networkSecurityGroup.name}.${resourceSuffix}', 64)
    params: {
      name: 'nsg-${resourceSuffix}-${subnet.?networkSecurityGroup.name}'
      location: location
      securityRules: subnet.?networkSecurityGroup.securityRules
      tags: tags
      enableTelemetry: enableTelemetry
    }
  }
]

// 2. Create VNet and subnets, with subnets associated with corresponding NSGs
// using AVM Virtual Network module
// https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/network/virtual-network

module virtualNetwork 'br/public:avm/res/network/virtual-network:0.7.0' = {
  name: take('avm.res.network.virtual-network.${name}', 64)
  params: {
    name: name
    location: location
    addressPrefixes: addressPrefixes
    subnets: [
      for (subnet, i) in subnets: {
        name: subnet.name
        addressPrefixes: subnet.?addressPrefixes
        networkSecurityGroupResourceId: !empty(subnet.?networkSecurityGroup) ? nsgs[i]!.outputs.resourceId : null
        privateEndpointNetworkPolicies: subnet.?privateEndpointNetworkPolicies
        privateLinkServiceNetworkPolicies: subnet.?privateLinkServiceNetworkPolicies
        delegation: subnet.?delegation
        routeTableResourceId: subnet.?routeTableResourceId
        serviceEndpointPolicies: subnet.?serviceEndpointPolicies
        serviceEndpoints: subnet.?serviceEndpoints
        defaultOutboundAccess: subnet.?defaultOutboundAccess
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

output name string = virtualNetwork.outputs.name
output resourceId string = virtualNetwork.outputs.resourceId

// combined output array that holds subnet details along with NSG information
output subnets subnetOutputType[] = [
  for (subnet, i) in subnets: {
    name: subnet.name
    resourceId: virtualNetwork.outputs.subnetResourceIds[i]
    nsgName: !empty(subnet.?networkSecurityGroup) ? subnet.?networkSecurityGroup.name : null
    nsgResourceId: !empty(subnet.?networkSecurityGroup) ? nsgs[i]!.outputs.resourceId : null
  }
]

// Dynamic outputs for individual subnets for backward compatibility
output webSubnetResourceId string = contains(map(subnets, subnet => subnet.name), 'web') ? virtualNetwork.outputs.subnetResourceIds[indexOf(map(subnets, subnet => subnet.name), 'web')] : ''
output pepsSubnetResourceId string = contains(map(subnets, subnet => subnet.name), 'peps') ? virtualNetwork.outputs.subnetResourceIds[indexOf(map(subnets, subnet => subnet.name), 'peps')] : ''
output bastionSubnetResourceId string = contains(map(subnets, subnet => subnet.name), 'AzureBastionSubnet') ? virtualNetwork.outputs.subnetResourceIds[indexOf(map(subnets, subnet => subnet.name), 'AzureBastionSubnet')] : ''
output jumpboxSubnetResourceId string = contains(map(subnets, subnet => subnet.name), 'jumpbox') ? virtualNetwork.outputs.subnetResourceIds[indexOf(map(subnets, subnet => subnet.name), 'jumpbox')] : ''

@export()
@description('Custom type definition for subnet resource information as output')
type subnetOutputType = {
  @description('The name of the subnet.')
  name: string

  @description('The resource ID of the subnet.')
  resourceId: string

  @description('The name of the associated network security group, if any.')
  nsgName: string?

  @description('The resource ID of the associated network security group, if any.')
  nsgResourceId: string?
}

@export()
@description('Custom type definition for subnet configuration')
type subnetType = {
  @description('Required. The Name of the subnet resource.')
  name: string

  @description('Required. Prefixes for the subnet.')  // Required to ensure at least one prefix is provided
  addressPrefixes: string[]   

  @description('Optional. The delegation to enable on the subnet.')
  delegation: string?

  @description('Optional. enable or disable apply network policies on private endpoint in the subnet.')
  privateEndpointNetworkPolicies: ('Disabled' | 'Enabled' | 'NetworkSecurityGroupEnabled' | 'RouteTableEnabled')?

  @description('Optional. Enable or disable apply network policies on private link service in the subnet.')
  privateLinkServiceNetworkPolicies: ('Disabled' | 'Enabled')?

  @description('Optional. Network Security Group configuration for the subnet.')
  networkSecurityGroup: networkSecurityGroupType?

  @description('Optional. The resource ID of the route table to assign to the subnet.')
  routeTableResourceId: string?

  @description('Optional. An array of service endpoint policies.')
  serviceEndpointPolicies: object[]?

  @description('Optional. The service endpoints to enable on the subnet.')
  serviceEndpoints: string[]?

  @description('Optional. Set this property to false to disable default outbound connectivity for all VMs in the subnet. This property can only be set at the time of subnet creation and cannot be updated for an existing subnet.')
  defaultOutboundAccess: bool?
}

@export()
@description('Custom type definition for network security group configuration')
type networkSecurityGroupType = {
  @description('Required. The name of the network security group.')
  name: string

  @description('Required. The security rules for the network security group.')
  securityRules: object[]
}
