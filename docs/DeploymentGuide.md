# Deployment Guide

## **Pre-requisites**

To deploy this solution accelerator, ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the necessary permissions to create **resource groups, resources, app registrations, and assign roles at the resource group level**. This should include Contributor role at the subscription level and  Role Based Access Control role on the subscription and/or resource group level. Follow the steps in [Azure Account Set Up](./AzureAccountSetUp.md).

Check the [Azure Products by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/?products=all&regions=all) page and select a **region** where the following services are available:

- Azure OpenAI Service
- Azure AI Search
- [Azure Semantic Search](./AzureSemanticSearchRegion.md)  

Here are some example regions where the services are available: East US, East US2, Australia East, UK South, France Central.

### **Important Note for PowerShell Users**

If you encounter issues running PowerShell scripts due to the policy of not being digitally signed, you can temporarily adjust the `ExecutionPolicy` by running the following command in an elevated PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This will allow the scripts to run for the current session without permanently changing your system's policy.



## Deployment Options & Steps

Pick from the options below to see step-by-step instructions for GitHub Codespaces, VS Code Dev Containers, and Local Environments.

| [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/document-generation-solution-accelerator) | [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/microsoft/document-generation-solution-accelerator) |
|---|---|

<details>
  <summary><b>Deploy in GitHub Codespaces</b></summary>

### GitHub Codespaces

You can run this solution using GitHub Codespaces. The button will open a web-based VS Code instance in your browser:

1. Open the solution accelerator (this may take several minutes):

    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/document-generation-solution-accelerator)

2. Accept the default values on the create Codespaces page.
3. Open a terminal window if it is not already open.
4. Continue with the [deploying steps](#deploying-with-azd).

</details>

<details>
  <summary><b>Deploy in VS Code</b></summary>

### VS Code Dev Containers

You can run this solution in VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed).
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/microsoft/document-generation-solution-accelerator)

3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
4. Continue with the [deploying steps](#deploying-with-azd).

</details>

<details>
  <summary><b>Deploy in your local Environment</b></summary>

### Local Environment

If you're not using one of the above options for opening the project, then you'll need to:

1. Make sure the following tools are installed:
    - [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.5) <small>(v7.0+)</small> - available for Windows, macOS, and Linux. (Required for Windows users only. Follow the steps [here](./PowershellSetup.md) to add it to the Windows PATH.)
    - [Azure Developer CLI (azd)](https://aka.ms/install-azd)
    - [Python 3.9+](https://www.python.org/downloads/)
    - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - [Git](https://git-scm.com/downloads)

2. Clone the repository or download the project code via command-line:

    ```shell
    azd init -t microsoft/document-generation-solution-accelerator/
    ```

3. Open the project folder in your terminal or editor.
4. Continue with the [deploying steps](#deploying-with-azd).

</details>

<br/>

Consider the following settings during your deployment to modify specific settings:

<details>
  <summary><b>Configurable Deployment Settings</b></summary>

When you start the deployment, most parameters will have **default values**, but you can update the following settings:[here](../docs/CustomizingAzdParameters.md):

| **Setting**                          | **Description**                                                                               | **Default Value**        |
| ------------------------------------ | --------------------------------------------------------------------------------------------- | ------------------------ |
| **Azure Region**                     | The region where resources will be created.                                                   | `eastus`                 |
| **Environment Name**                 | A **3–20 character alphanumeric** value used to generate a unique ID to prefix the resources. | `byctemplate`            |
| **Secondary Location**               | A **less busy** region for **CosmosDB**, useful in case of availability constraints.          | `eastus2`                |
| **Deployment Type**                  | Model deployment type (allowed: `Standard`, `GlobalStandard`).                                | `GlobalStandard`         |
| **GPT Model**                        | The GPT model used by the app                                                                 | `gpt-4.1`                |
| **GPT Model Version**                | The GPT Version used by the app                                                               | `2024-05-13`             |
| **OpenAI API Version**               | Azure OpenAI API version used for deployments.                                                | `2024-05-01-preview`     |
| **GPT Model Deployment Capacity**    | Configure the capacity for **GPT model deployments** (in thousands).                          | `30k`                    |
| **Embedding Model**                  | The embedding model used by the app.                                                          | `text-embedding-ada-002` |
| **Embedding Model Capacity**         | Configure the capacity for **embedding model deployments** (in thousands).                    | `80k`                    |
| **Image Tag**                        | Image version for deployment (allowed: `latest`, `dev`, `hotfix`).                            | `latest`                 |
| **Existing Log Analytics Workspace** | If reusing a Log Analytics Workspace, specify the ID.                                         | *(none)*                 |



</details>

<details>
  <summary><b>[Optional] Quota Recommendations</b></summary>

By default, the _Gpt-4.1 model capacity_ in deployment is set to _30k tokens_, so we recommend:
- **For Global Standard | GPT-4.1** - the capacity to at least 150k tokens post-deployment for optimal performance.

- **For Standard | GPT-4** - ensure a minimum of 30k–40k tokens for best results.

To adjust quota settings, follow these [steps](./AzureGPTQuotaSettings.md).

### ⚠️ Important: Check Azure OpenAI Quota Availability  

➡️ To ensure sufficient quota is available in your subscription, please follow **[Quota check instructions guide](./QuotaCheck.md)** before you deploy the solution. Insufficient quota can cause deployment errors. Please ensure you have the recommended capacity or request additional capacity before deploying this solution. 

</details>

<details>

  <summary><b>Reusing an Existing Log Analytics Workspace</b></summary>

  To configure your environment to use an existing Log Analytics Workspace, follow these steps:

  #### 1. Navigate to Azure Portal
  Go to [Azure Portal](https://portal.azure.com)

  #### 2. Find Your Log Analytics Workspace
  - In the search bar at the top, type "Log Analytics workspaces" and select it.
  - Click on the workspace  you want to use.

  ![Log Analytics Resource List](../docs/images/logAnalyticsList.png)

  #### 3. Copy Workspace Id
  - In the Overview pane, Click on **JSON View**

  ![Log Analytics](../docs/images/logAnalytics.png)

  - Copy the **Resource ID** (this is your Workspace ID)

  ![Log Analytics JSON](../docs/images/logAnalyticsJson.png)

  #### 4. Set the Workspace ID in Your Environment
  Run the following command in your terminal
  ```bash
  azd env set AZURE_ENV_LOG_ANALYTICS_WORKSPACE_ID '<Existing Log Analytics Workspace Id>'
  ```
  Replace `<Existing Log Analytics Workspace Id>` with the full Resource ID obtained from Step 3.

  #### 5. Continue Deployment
  Continue with the [deploying steps](#deploying-with-azd).

</details>

### Deploying with AZD

Once you've opened the project in [Codespaces](#github-codespaces), [Dev Containers](#vs-code-dev-containers), or [locally](#local-environment), you can deploy it to Azure by following these steps:

1. Login to Azure:

    ```shell
    azd auth login
    ```

    #### To authenticate with Azure Developer CLI (`azd`), use the following command with your **Tenant ID**:

    ```sh
    azd auth login --tenant-id <tenant-id>
    ```

2. Provision and deploy all the resources:

    ```shell
    azd up
    ```

3. Provide an `azd` environment name (e.g., "dgapp").
4. Select a subscription from your Azure account and choose a location that has quota for all the resources. 
    - This deployment will take *7-10 minutes* to provision the resources in your account and set up the solution with sample data.
    - If you encounter an error or timeout during deployment, changing the location may help, as there could be availability constraints for the resources.

5. Once the deployment has completed successfully and you would like to use the sample data, run the bash command printed in the terminal. The bash command will look like the following: 
    ```shell 
    bash ./infra/scripts/process_sample_data.sh
    ```
    If you don't have azd env then you need to pass parameters along with the command. Then the command will look like the following:
    ```shell 
    bash ./infra/scripts/process_sample_data.sh <Storage-Account-name> <Storage-Account-container-name> <Key-Vault-name> <CosmosDB-Account-name> <Resource-Group-name> <aiFoundryResourceName> <aiSearchResourceName>
    ```

6. Open the [Azure Portal](https://portal.azure.com/), go to the deployed resource group, find the App Service and get the app URL from `Default domain`.

7. You can now delete the resources by running `azd down`, if you are done trying out the application. 

## Post Deployment Steps

1. **Add App Authentication**

     > Note: Authentication changes can take up to 10 minutes 

    Follow steps in [App Authentication](./AppAuthentication.md) to configure authentication in app service.

2. **Deleting Resources After a Failed Deployment**  

     - Follow steps in [Delete Resource Group](./DeleteResourceGroup.md) if your deployment fails and/or you need to clean up the resources.

## Next Steps
Now that you've completed your deployment, you can start using the solution. 

To help you get started, here are some [Sample Questions](./SampleQuestions.md) you can follow to try it out.
