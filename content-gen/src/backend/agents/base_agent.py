"""
Base Agent Factory for the Content Generation Accelerator.

Provides a singleton pattern for agent creation with async lock
to ensure thread-safe initialization.

Uses Azure AI Agents SDK for agent orchestration.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import Agent

from backend.settings import app_settings

logger = logging.getLogger(__name__)


def get_azure_credential(client_id: Optional[str] = None):
    """Get Azure credential for operations."""
    if client_id:
        return ManagedIdentityCredential(client_id=client_id)
    return DefaultAzureCredential()


class BaseAgentFactory(ABC):
    """
    Abstract base factory for creating and managing agent instances.
    
    Uses singleton pattern with async lock to ensure only one instance
    of each agent type exists per application lifecycle.
    """
    
    _lock: asyncio.Lock = asyncio.Lock()
    _agent: Optional[Agent] = None
    _project_client: Optional[AIProjectClient] = None
    
    @classmethod
    def get_project_client(cls) -> AIProjectClient:
        """Get or create the Azure AI Project client."""
        if cls._project_client is None:
            credential = get_azure_credential(
                client_id=app_settings.base_settings.azure_client_id
            )
            # Use the agent endpoint if configured, otherwise use OpenAI endpoint
            endpoint = app_settings.azure_ai.agent_endpoint or app_settings.azure_openai.endpoint
            if endpoint is None:
                raise ValueError("No agent endpoint or OpenAI endpoint configured")
            cls._project_client = AIProjectClient(
                credential=credential,
                endpoint=endpoint,
            )
        return cls._project_client
    
    @classmethod
    @abstractmethod
    async def create_agent(cls) -> Agent:
        """Create the specific agent instance. Must be implemented by subclasses."""
        pass
    
    @classmethod
    @abstractmethod
    def get_agent_name(cls) -> str:
        """Return the agent's name. Must be implemented by subclasses."""
        pass
    
    @classmethod
    @abstractmethod
    def get_agent_instructions(cls) -> str:
        """Return the agent's system instructions. Must be implemented by subclasses."""
        pass
    
    @classmethod
    async def get_agent(cls) -> Agent:
        """Get or create the singleton agent instance."""
        async with cls._lock:
            if cls._agent is None:
                logger.info(f"Creating {cls.get_agent_name()} agent...")
                cls._agent = await cls.create_agent()
                logger.info(f"{cls.get_agent_name()} agent created successfully")
            return cls._agent
    
    @classmethod
    async def delete_agent(cls) -> None:
        """Clean up the agent instance."""
        async with cls._lock:
            if cls._agent is not None:
                logger.info(f"Deleting {cls.get_agent_name()} agent...")
                cls._agent = None
                cls._project_client = None
