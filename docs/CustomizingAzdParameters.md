## [Optional]: Customizing resource names 

By default this template will use the environment name as the prefix to prevent naming collisions within Azure. The parameters below show the default values. You only need to run the statements below if you need to change the values. 


> To override any of the parameters, run `azd env set <PARAMETER_NAME> <VALUE>` before running `azd up`. On the first azd command, it will prompt you for the environment name. Be sure to choose 3-20 charaters alphanumeric unique name. 

## Parameters

| Name                                   | Type    | Example Value                | Purpose                                                                       |
| -------------------------------------- | ------- | ---------------------------- | ----------------------------------------------------------------------------- |
| `AZURE_LOCATION`                       | string  | `japaneast` | Sets the Azure region for resource deployment.                                |
| `AZURE_ENV_NAME`                       | string  | `docgen`                   | Sets the environment name prefix for all Azure resources.                     |
| `AZURE_ENV_SECONDARY_LOCATION`         | string  | `eastus2`                  | Specifies a secondary Azure region.                                           |
| `AZURE_ENV_MODEL_DEPLOYMENT_TYPE`      | string  | `Standard`                 | Defines the model deployment type (allowed: `Standard`, `GlobalStandard`).    |
| `AZURE_ENV_MODEL_NAME`                 | string  | `gpt-4.1`                   | Specifies the GPT model name (allowed: `gpt-4.1`).                    |
| `AZURE_ENV_MODEL_VERSION`                 | string  | `2024-05-13`                   | Set the Azure model version (allowed values: `2024-08-06`).                    |
| `AZURE_ENV_OPENAI_API_VERSION`                 | string  | `2024-05-01-preview`                   | Specifies the API version for Azure OpenAI.                    |
| `AZURE_ENV_MODEL_CAPACITY`             | integer | `30`                         | Sets the GPT model capacity (based on what's available in your subscription). |
| `AZURE_ENV_EMBEDDING_MODEL_NAME`       | string  | `text-embedding-ada-002`   | Sets the name of the embedding model to use.                                  |
| `AZURE_ENV_IMAGETAG`       | string  | `latest`   | Set the Image tag Like (allowed values: latest, dev, hotfix)                                   |
| `AZURE_ENV_EMBEDDING_MODEL_CAPACITY`   | integer | `80`                         | Sets the capacity for the embedding model deployment.                         |
| `AZURE_ENV_LOG_ANALYTICS_WORKSPACE_ID` | string  | Guide to get your [Existing Workspace ID](/docs/re-use-log-analytics.md)  | Reuses an existing Log Analytics Workspace instead of creating a new one.     |



## How to Set a Parameter


To customize any of the above values, run the following command **before** `azd up`:

```bash
azd env set <PARAMETER_NAME> <VALUE>
```

**Example:**

```bash
azd env set AZURE_LOCATION westus2
```
