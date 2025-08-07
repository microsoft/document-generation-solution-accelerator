@minLength(3)
@maxLength(15)
@description('Solution Name')
param solutionName string

@description('Specifies the location for resources.')
param solutionLocation string

@description('Base URL')
param baseUrl string

@description('Contains Managed Identity Object ID')
param managedIdentityObjectId string

@description('Contains Managed Identity Client ID')
param managedIdentityClientId string

@description('Contains Storage Account Name')
param storageAccountName string

@description('Contains Container Name')
param containerName string

@description('Contains Container App Name')
param containerAppName string = 'ca-${ solutionName }'

@description('Contains Environment Name')
param environmentName string = 'cae-${ solutionName }'

@description('Image Name')
param imageName string = 'python:3.11-alpine'

@description('Contains SetupCopyKBFiles')
param setupCopyKbFiles string = '${baseUrl}infra/scripts/copy_kb_files.sh'

@description('Contains URL of SetupCreateIndex Script')
param setupCreateIndexScriptsUrl string = '${baseUrl}infra/scripts/run_create_index_scripts.sh'

@description('Contains KeyVault Name')
param keyVaultName string

@description('Contains Log Analytics Workspace Resource Name')
param logAnalyticsWorkspaceResourceName string

@description('Optional. Tags to be applied to the resources.')
param tags object = {}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2020-10-01' existing = {
  name: logAnalyticsWorkspaceResourceName
  scope: resourceGroup()
}
resource containerAppEnv 'Microsoft.App/managedEnvironments@2022-03-01' = {
  name: environmentName
  location: solutionLocation
  properties: {
    zoneRedundant: false
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
  tags : tags
}

resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: containerAppName
  location: solutionLocation
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityObjectId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: null
      activeRevisionsMode: 'Single'
    }
    template: {
      scale:{
        minReplicas: 1
        maxReplicas: 1
      }
      containers: [
        {
          name: containerAppName
          image: imageName
          resources: {
            cpu: 2
            memory: '4.0Gi'
          }
          command: [
            '/bin/sh', '-c', 'mkdir -p /scripts && apk add --no-cache curl bash jq py3-pip gcc musl-dev libffi-dev openssl-dev python3-dev && pip install --upgrade azure-cli && apk add --no-cache --virtual .build-deps build-base unixodbc-dev && curl -s -o msodbcsql18_18.4.1.1-1_amd64.apk https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/msodbcsql18_18.4.1.1-1_amd64.apk && curl -s -o mssql-tools18_18.4.1.1-1_amd64.apk https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/mssql-tools18_18.4.1.1-1_amd64.apk && apk add --allow-untrusted msodbcsql18_18.4.1.1-1_amd64.apk && apk add --allow-untrusted mssql-tools18_18.4.1.1-1_amd64.apk && curl -s -o /scripts/copy_kb_files.sh ${setupCopyKbFiles} && chmod +x /scripts/copy_kb_files.sh && sh -x /scripts/copy_kb_files.sh ${storageAccountName} ${containerName} ${baseUrl} ${managedIdentityClientId} && curl -s -o /scripts/run_create_index_scripts.sh ${setupCreateIndexScriptsUrl} && chmod +x /scripts/run_create_index_scripts.sh && sh -x /scripts/run_create_index_scripts.sh ${baseUrl} ${keyVaultName} ${managedIdentityClientId} && apk add --no-cache ca-certificates less ncurses-terminfo-base krb5-libs libgcc libintl libssl3 libstdc++ tzdata userspace-rcu zlib icu-libs curl && apk -X https://dl-cdn.alpinelinux.org/alpine/edge/main add --no-cache lttng-ust openssh-client && echo "Container app setup completed successfully."'
          ]
          env: [
            {
              name: 'STORAGE_ACCOUNT_NAME'
              value: storageAccountName
            }
            {
              name: 'CONTAINER_NAME'
              value: containerName
            }
            {
              name:'APPSETTING_WEBSITE_SITE_NAME'
              value:'DUMMY'
            }
          ]
        }
      ]
    }
  }
  tags : tags
}
