# Agent Creation Scripts

This directory contains scripts for automating the creation and registration of AI agents as a post-deployment step for the Document Generation Solution Accelerator.

## Overview

The agent creation automation uses **Azure AI Projects SDK 2.0** (Agent Framework v2) to provision and configure agents immediately after infrastructure deployment, ensuring they are ready for use without manual intervention.

## Files

- **`01_create_agents.py`** - Python script that creates and registers agents with Azure AI Foundry
- **`run_create_agents_scripts.sh`** - Bash orchestration script that handles the complete agent creation workflow
- **`requirements.txt`** - Python dependencies for agent creation (Azure AI Projects SDK 2.0)

## Usage

### Automatic Execution (Recommended)

After running `azd up`, follow the post-deployment instructions displayed in the terminal:

```bash
bash ./infra/scripts/agent_scripts/run_create_agents_scripts.sh
```

The script will automatically:
1. Retrieve deployment parameters from the azd environment
2. Check and assign required Azure roles
3. Temporarily enable public network access if needed
4. Create and register agents
5. Update App Service environment variables
6. Restore original network settings

### Manual Execution

You can also run the script manually with explicit parameters:

```bash
bash ./infra/scripts/agent_scripts/run_create_agents_scripts.sh \
  <projectEndpoint> \
  <solutionName> \
  <gptModelName> \
  <aiFoundryResourceId> \
  <apiAppName> \
  <aiSearchConnectionName> \
  <aiSearchIndex> \
  <resourceGroup>
```

## Agents Created

### 1. Document Generation Agent
- **Name Pattern**: `DocGen-DocumentAgent-{solutionName}`
- **Purpose**: Assists users with document creation, analysis, and management
- **Tools**: Azure AI Search integration for retrieving relevant information from indexed documents
- **Features**:
  - Citation-based responses with inline references
  - Document retrieval and analysis
  - Contextual information extraction

### 2. Title Generation Agent
- **Name Pattern**: `DocGen-TitleAgent-{solutionName}`
- **Purpose**: Generates concise, meaningful titles for conversations and documents
- **Output**: 4-word or less titles capturing core intent

## Prerequisites

- Azure CLI installed and authenticated
- Python 3.8 or higher
- Access to Azure AI Foundry project
- Azure AI User role on the AI Foundry resource (automatically assigned by the script)

## Environment Variables Set

After successful execution, the following environment variables are set:

- `AGENT_NAME_DOCUMENT` - Name of the document generation agent
- `AGENT_NAME_TITLE` - Name of the title generation agent

These are stored in:
- Azure App Service application settings
- Azd environment configuration

## SDK Version

This implementation uses:
- **azure-ai-projects==2.0.0b2** (Agent Framework SDK 2.0)
- **azure-identity==1.23.0**

## Network Configuration

The script automatically handles network access requirements:
- Temporarily enables public network access for AI Foundry if private networking is configured
- Restores original network settings after agent creation
- Includes error handling and cleanup on script exit

## Troubleshooting

### Role Assignment Issues
If you encounter permission errors, ensure your account has:
- Contributor role on the resource group
- Owner or User Access Administrator role to assign the Azure AI User role

### Network Access Issues
If agent creation fails with connectivity errors:
- Check if AI Foundry has network restrictions
- Verify the script successfully enabled public access temporarily
- Check Azure Portal for any firewall rules blocking access

### Agent Creation Failures
If agents fail to create:
- Verify the AI Project endpoint is correct
- Ensure the GPT model deployment exists and is accessible
- Check AI Search connection and index are properly configured

## Integration with Deployment

This automation is integrated into the deployment workflow via `azure.yaml` post-provision hooks, making it part of the standard deployment process across all applicable accelerators.

## References

- [Azure AI Projects SDK Documentation](https://learn.microsoft.com/azure/ai-foundry/reference/python/azure-ai-projects/)
- [Agent Framework Transparency FAQ](https://github.com/microsoft/agent-framework/blob/main/TRANSPARENCY_FAQ.md)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
