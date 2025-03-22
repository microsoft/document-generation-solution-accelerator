# Document Generation Solution Accelerator

MENU: [**USER STORY**](#user-story) \| [**QUICK DEPLOY**](#quick-deploy) \| [**SUPPORTING DOCUMENTATION**](#supporting-documentation)


<h2><img src="./docs/images/userStory.png" width="64">
<br/>
User story
</h2>

**Solution accelerator overview**

This solution accelerator is a powerful tool that helps you create your own AI assistant for document generation. The accelerator can be used by any customer looking for reusable architecture and code snippets to build an AI assistant to generate a sample template and content grounded on their own enterprise data. 

It leverages Azure OpenAI Service and Azure AI Search, to identify relevant documents, summarize unstructured information, and generate document templates. 


### Key features

![Key Features](/docs/images/keyfeatures.png)

Below is an image of the solution. 

![Landing Page](/docs/images/landing_page.png)

**Scenario**

This example focuses on a generic use case - chat with your own data, generate a document template using your own data, and exporting the document in a docx format.

The sample data is sourced from generic AI-generated promissory notes.
The documents are intended for use as sample data only.


### Solution accelerator architecture
![image](/docs/images/Archimage.png)

<h2><img src="./docs/images/oneClickDeploy.png" width="64">
<br/>
QUICK DEPLOY
</h2>

### Prerequisites

To deploy this solution accelerator, ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the necessary permissions to create **resource groups and resources**. Follow the steps in  [Azure Account Set Up](./docs/AzureAccountSetUp.md) 

Check the [Azure Products by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/?products=all&regions=all) page and select a **region** where the following services are available:  

- Azure AI Foundry 
- Azure OpenAI Service
- Azure AI Search
- Embedding Model Capacity  
- GPT Model Capacity
- [Azure Semantic Search](./docs/AzureSemanticSearchRegion.md)  

Here are some example regions where the services are available: East US, East US2, Australia East, UK South, France Central.

### ⚠️ Important: Check Azure OpenAI Quota Availability  

➡️ To ensure sufficient quota is available in your subscription, please follow **[Quota check instructions guide](./docs/quota_check.md)** before you deploy the solution.

<!-- Here are some example regions where the services are available: East US, East US2, Australia East, UK South, France Central. -->
<!-- 
| [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fdocument-generation-solution-accelerator%2Fmain%2Finfra%2Fmain.json) |
|---|
-->

| [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/document-generation-solution-accelerator) | [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/microsoft/document-generation-solution-accelerator) | 
|---|---|

### Configurable Deployment Settings

When you start the deployment, most parameters will have **default values**, but you can update the following settings:  

| **Setting** | **Description** |  **Default value** |
|------------|----------------|  ------------|
| **Azure Region** | The region where resources will be created. | East US| 
| **Environment Name** | A **3-20 character alphanumeric value** used to generate a unique ID to prefix the resources. |  byctemplate |
| **Secondary Location** | A **less busy** region for **Azure SQL and CosmosDB**, useful in case of availability constraints. |  eastus2 |
| **Deployment Type** | Select from a drop-down list. |  Standard |
| **GPT Model** | Choose from **gpt-4, gpt-4o** | gpt-4 |  
| **GPT Model Deployment Capacity** | Configure capacity for **GPT models**. | 30k |
| **Embedding Model** | Default: **text-embedding-ada-002**. |  text-embedding-ada-002 |
| **Embedding Model Capacity** | Set the capacity for **embedding models**. |  80k |


### [Optional] Quota Recommendations  
By default, the **GPT model capacity** in deployment is set to **30k tokens**.  
> **We recommend increasing the capacity to 100k tokens for optimal performance.** 

To adjust quota settings, follow these [steps](./docs/AzureGPTQuotaSettings.md)  

### Deployment Options
Pick from the options below to see step-by-step instructions for: GitHub Codespaces, VS Code Dev Containers, Local Environments, and Bicep deployments.

<details>
  <summary><b>Deploy in GitHub Codespaces</b></summary>

### GitHub Codespaces

You can run this solution using GitHub Codespaces. The button will open a web-based VS Code instance in your browser:

1. Open the solution accelerator (this may take several minutes):

    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/document-generation-solution-accelerator)
2. Accept the default values on the create Codespaces page
3. Open a terminal window if it is not already open
4. Continue with the [deploying steps](#deploying)

</details>

<details>
  <summary><b>Deploy in VS Code</b></summary>

 ### VS Code Dev Containers

You can run this solution in VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/microsoft/document-generation-solution-accelerator)


3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
4. Continue with the [deploying steps](#deploying)

</details>

<details>
  <summary><b>Deploy in your local environment</b></summary>

 ### Local environment

If you're not using one of the above options for opening the project, then you'll need to:

1. Make sure the following tools are installed:

    * [Azure Developer CLI (azd)](https://aka.ms/install-azd)
    * [Python 3.9+](https://www.python.org/downloads/)
    * [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    * [Git](https://git-scm.com/downloads)

2. Download the project code:

    ```shell
    azd init -t microsoft/document-generation-solution-accelerator/
    ```

3. Open the project folder in your terminal or editor.

4. Continue with the [deploying steps](#deploying).

</details>

<!-- <details>
  <summary><b>Deploy with Bicep/ARM template</b></summary>
 ### Bicep
 
   Click the following deployment button to create the required resources for this solution directly in your Azure Subscription.

   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fdocument-generation-solution-accelerator%2Fmain%2Finfra%2Fmain.json)          

</details> -->


### Deploying

Once you've opened the project in [Codespaces](#github-codespaces) or in [Dev Containers](#vs-code-dev-containers) or [locally](#local-environment), you can deploy it to Azure following the following steps. 

To change the azd parameters from the default values, follow the steps [here](./docs/CustomizingAzdParameters.md). 


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

3. Provide an `azd` environment name (like "bycapp")
4. Select a subscription from your Azure account, and select a location which has quota for all the resources. 
    * This deployment will take *7-10 minutes* to provision the resources in your account and set up the solution with sample data. 
    * If you get an error or timeout with deployment, changing the location can help, as there may be availability constraints for the resources.

5. Once the deployment has completed successfully, open the [Azure Portal](https://portal.azure.com/), go to the deployed resource group, find the App Service and get the app URL from `Default domain`.

6. You can now delete the resources by running `azd down`, if you are done trying out the application. 
<!-- 6. You can now proceed to run the [development server](#development-server) to test the app locally, or if you are done trying out the app, you can delete the resources by running `azd down`. -->

<h2>
Additional Steps
</h2>

1. **Add App Authentication**
   
    Follow steps in [App Authentication](./docs/AppAuthentication.md) to configure authenitcation in app service.

    Note: Authentication changes can take up to 10 minutes 

2. **Deleting Resources After a Failed Deployment**

     Follow steps in [Delete Resource Group](./docs/DeleteResourceGroup.md) If your deployment fails and you need to clean up the resources.



<!-- 

### **How to install/deploy**

1. Please check the link [Azure Products by Region](
https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/?products=all&regions=all) and choose a region where Azure AI Search, Azure OpenAI Service, and Azure AI Foundry are available. If you are using the included sample data set, verify Document Intelligence (Form Recognizer) is available.

2. Click the following deployment button to create the required resources for this accelerator in your Azure Subscription.

   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fdocument-generation-solution-accelerator%2Fmain%2Finfrastructure%2Fdeployment.json)

3. You will need to select an Azure Subscription, create/select a Resource group, and Region. If your intention is to deploy this solution accelerator and the corresponding sample data set, the default settings will suffice.

If you are using your own data, the next step is optional.

4. Follow steps in [Sample data guide](./scripts/SAMPLE_DATA.md) to ingest the sample Promissory Note PDFs into the search index.

If you want to enable authentication, you will need to add an identity provider.

#### Add an identity provider
After deployment, you will need to add an identity provider to provide authentication support in your app. See [this tutorial](https://learn.microsoft.com/en-us/azure/app-service/scenario-secure-app-authentication-app-service) for more information.

If you don't add an identity provider, the chat functionality will allow anyone to access the chat functionality of your app. **This is not recommended for production apps.** To enable this restriction, you can add `AUTH_ENABLED=True` to the environment variables. This will enable authentication and prevent unauthorized access to the chat functionality of your app.

To add further access controls, update the logic in `getUserInfoList` in `frontend/src/pages/chat/Chat.tsx`. 

#### Recommended practices
1. **For enhanced relevance and accuracy**, we recommend implementing [Azure hybrid search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview) over full-text search. Azure hybrid search provides superior relevance, accuracy, support for complex queries, improved user experience, scalability, performance, advanced features, and integration with AI services. These advantages make it the ideal choice for modern applications that require robust and intelligent search capabilities.
2. **Importance of prompt engineering**. Prompt engineering is a critical aspect of working with AI models, especially when leveraging advanced capabilities such as those provided by Azure AI services. Proper prompt engineering ensures that the AI models generate accurate, relevant, and contextually appropriate responses. It involves carefully crafting and refining prompts to guide the model's behavior and output effectively. Neglecting prompt engineering can result in suboptimal performance, irrelevant outputs, and increased frustration for users. Therefore, it is essential to invest time and effort in prompt engineering to fully harness the potential of AI models

### Local deployment
Review the local deployment [README](./docs/README_LOCAL.md). -->



<h2>
</br>
Responsible AI Transparency FAQ 
</h2>

Please refer to [Transparency FAQ](./docs/TRANSPARENCY_FAQ.md) for responsible AI transparency details of this solution accelerator.

<h2>
Supporting documentation
</h2>

### Costs

Pricing varies per region and usage, so it isn't possible to predict exact costs for your usage.
The majority of the Azure resources used in this infrastructure are on usage-based pricing tiers.
However, Azure Container Registry has a fixed cost per registry per day.

You can try the [Azure pricing calculator](https://azure.microsoft.com/en-us/pricing/calculator) for the resources:

* Azure AI Foundry: Free tier. [Pricing](https://azure.microsoft.com/pricing/details/ai-studio/)
* Azure AI Search: Standard tier, S1. Pricing is based on the number of documents and operations. [Pricing](https://azure.microsoft.com/pricing/details/search/)
* Azure Storage Account: Standard tier, LRS. Pricing is based on storage and operations. [Pricing](https://azure.microsoft.com/pricing/details/storage/blobs/)
* Azure Key Vault: Standard tier. Pricing is based on the number of operations. [Pricing](https://azure.microsoft.com/pricing/details/key-vault/)
* Azure AI Services: S0 tier, defaults to gpt-4o and text-embedding-ada-002 models. Pricing is based on token count. [Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/)
* Azure Container App: Consumption tier with 0.5 CPU, 1GiB memory/storage. Pricing is based on resource allocation, and each month allows for a certain amount of free usage. [Pricing](https://azure.microsoft.com/pricing/details/container-apps/)
* Azure Container Registry: Basic tier. [Pricing](https://azure.microsoft.com/pricing/details/container-registry/)
* Log analytics: Pay-as-you-go tier. Costs based on data ingested. [Pricing](https://azure.microsoft.com/pricing/details/monitor/)
* Azure Cosmos DB: [Pricing](https://azure.microsoft.com/en-us/pricing/details/cosmos-db/autoscale-provisioned/)


⚠️ To avoid unnecessary costs, remember to take down your app if it's no longer in use,
either by deleting the resource group in the Portal or running `azd down`.

### Security guidelines

This template uses Azure Key Vault to store all connections to communicate between resources.

This template also uses [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) for local development and deployment.

To ensure continued best practices in your own repository, we recommend that anyone creating solutions based on our templates ensure that the [Github secret scanning](https://docs.github.com/code-security/secret-scanning/about-secret-scanning) setting is enabled.

You may want to consider additional security measures, such as:

* Enabling Microsoft Defender for Cloud to [secure your Azure resources](https://learn.microsoft.com/azure/security-center/defender-for-cloud).
* Protecting the Azure Container Apps instance with a [firewall](https://learn.microsoft.com/azure/container-apps/waf-app-gateway) and/or [Virtual Network](https://learn.microsoft.com/azure/container-apps/networking?tabs=workload-profiles-env%2Cazure-cli).



### Additional Resources
1. [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/) 
2. [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/) 
3. [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/)

## Disclaimers

This release is an artificial intelligence (AI) system that generates text based on user input. The text generated by this system may include ungrounded content, meaning that it is not verified by any reliable source or based on any factual data. The data included in this release is synthetic, meaning that it is artificially created by the system and may contain factual errors or inconsistencies. Users of this release are responsible for determining the accuracy, validity, and suitability of any content generated by the system for their intended purposes. Users should not rely on the system output as a source of truth or as a substitute for human judgment or expertise.

This release only supports English language input and output. Users should not attempt to use the system with any other language or format. The system output may not be compatible with any translation tools or services, and may lose its meaning or coherence if translated.

This release does not reflect the opinions, views, or values of Microsoft Corporation or any of its affiliates, subsidiaries, or partners. The system output is solely based on the system's own logic and algorithms, and does not represent any endorsement, recommendation, or advice from Microsoft or any other entity. Microsoft disclaims any liability or responsibility for any damages, losses, or harms arising from the use of this release or its output by any user or third party.

This release does not provide any financial advice, and is not designed to replace the role of qualified client advisors in appropriately advising clients. Users should not use the system output for any financial decisions or transactions, and should consult with a professional financial advisor before taking any action based on the system output. Microsoft is not a financial institution or a fiduciary, and does not offer any financial products or services through this release or its output.

This release is intended as a proof of concept only, and is not a finished or polished product. It is not intended for commercial use or distribution, and is subject to change or discontinuation without notice. Any planned deployment of this release or its output should include comprehensive testing and evaluation to ensure it is fit for purpose and meets the user's requirements and expectations. Microsoft does not guarantee the quality, performance, reliability, or availability of this release or its output, and does not provide any warranty or support for it.

This Software requires the use of third-party components which are governed by separate proprietary or open-source licenses as identified below, and you must comply with the terms of each applicable license in order to use the Software. You acknowledge and agree that this license does not grant you a license or other right to use any such third-party proprietary or open-source components.

To the extent that the Software includes components or code used in or derived from Microsoft products or services, including without limitation Microsoft Azure Services (collectively, “Microsoft Products and Services”), you must also comply with the Product Terms applicable to such Microsoft Products and Services. You acknowledge and agree that the license governing the Software does not grant you a license or other right to use Microsoft Products and Services. Nothing in the license or this ReadMe file will serve to supersede, amend, terminate or modify any terms in the Product Terms for any Microsoft Products and Services.

You must also comply with all domestic and international export laws and regulations that apply to the Software, which include restrictions on destinations, end users, and end use. For further information on export restrictions, visit https://aka.ms/exporting.

You acknowledge that the Software and Microsoft Products and Services (1) are not designed, intended or made available as a medical device(s), and (2) are not designed or intended to be a substitute for professional medical advice, diagnosis, treatment, or judgment and should not be used to replace or as a substitute for professional medical advice, diagnosis, treatment, or judgment. Customer is solely responsible for displaying and/or obtaining appropriate consents, warnings, disclaimers, and acknowledgements to end users of Customer’s implementation of the Online Services.

You acknowledge the Software is not subject to SOC 1 and SOC 2 compliance audits. No Microsoft technology, nor any of its component technologies, including the Software, is intended or made available as a substitute for the professional advice, opinion, or judgement of a certified financial services professional. Do not use the Software to replace, substitute, or provide professional financial advice or judgment.

BY ACCESSING OR USING THE SOFTWARE, YOU ACKNOWLEDGE THAT THE SOFTWARE IS NOT DESIGNED OR INTENDED TO SUPPORT ANY USE IN WHICH A SERVICE INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE COULD RESULT IN THE DEATH OR SERIOUS BODILY INJURY OF ANY PERSON OR IN PHYSICAL OR ENVIRONMENTAL DAMAGE (COLLECTIVELY, “HIGH-RISK USE”), AND THAT YOU WILL ENSURE THAT, IN THE EVENT OF ANY INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE, THE SAFETY OF PEOPLE, PROPERTY, AND THE ENVIRONMENT ARE NOT REDUCED BELOW A LEVEL THAT IS REASONABLY, APPROPRIATE, AND LEGAL, WHETHER IN GENERAL OR IN A SPECIFIC INDUSTRY. BY ACCESSING THE SOFTWARE, YOU FURTHER ACKNOWLEDGE THAT YOUR HIGH-RISK USE OF THE SOFTWARE IS AT YOUR OWN RISK.  
