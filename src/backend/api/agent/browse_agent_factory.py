import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.identity.aio import DefaultAzureCredential
from backend.settings import app_settings


class BrowseAgentFactory:
    _lock = asyncio.Lock()
    _agent_data = None

    @classmethod
    async def get_browse_agent(cls, system_instruction: str):
        async with cls._lock:
            if cls._agent_data is None:
                print("Initializing browse agent and index...", flush=True)

                client = AIProjectClient(
                    endpoint=app_settings.azure_ai.agent_endpoint,
                    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
                    api_version="2025-05-01"
                )

                index_name = f"project-index-{app_settings.datasource.connection_name}-{app_settings.datasource.index}"
                index_version = "1"
                field_mapping = {
                    "contentFields": ["content"],
                    "urlField": "sourceurl",
                    "titleField": "sourceurl",
                }

                project_index = await client.indexes.create_or_update(
                    name=index_name,
                    version=index_version,
                    body={
                        "connectionName": app_settings.datasource.connection_name,
                        "indexName": app_settings.datasource.index,
                        "type": "AzureSearch",
                        "fieldMapping": field_mapping
                    }
                )

                ai_search = AzureAISearchTool(
                    index_asset_id=f"{project_index.name}/versions/{project_index.version}",
                    index_connection_id=None,
                    index_name=None,
                    query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,
                    top_k=app_settings.datasource.top_k,
                    filter="",
                )

                agent = await client.agents.create_agent(
                    model=app_settings.azure_ai.agent_model_deployment_name,
                    name="DocGenAgent",
                    instructions=system_instruction,
                    tools=ai_search.definitions,
                    tool_resources=ai_search.resources,
                )

                cls._agent_data = {
                    "client": client,
                    "agent": agent
                }

        return cls._agent_data
