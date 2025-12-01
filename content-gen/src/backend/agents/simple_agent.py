"""
Simple Agent implementation using Azure OpenAI directly.

This provides a working implementation that can be upgraded to
Azure AI Agents SDK when production-ready.
"""

import json
import logging
from typing import Any, Callable, List, Optional

from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential

from backend.settings import app_settings

logger = logging.getLogger(__name__)


class SimpleAgent:
    """
    A simple agent that uses Azure OpenAI chat completions.
    
    This is a lightweight implementation suitable for development
    and can be replaced with Azure AI Agents SDK for production.
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
    ):
        self.name = name
        self.instructions = instructions
        self.model = model or app_settings.azure_openai.gpt_model
        self.tools = tools or []
        self._client: Optional[AsyncAzureOpenAI] = None
    
    async def _get_client(self) -> AsyncAzureOpenAI:
        """Get or create the Azure OpenAI client."""
        if self._client is None:
            endpoint = app_settings.azure_openai.endpoint
            if not endpoint:
                raise ValueError("Azure OpenAI endpoint is not configured")
            
            client_id = app_settings.base_settings.azure_client_id
            if client_id:
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = DefaultAzureCredential()
            
            token = await credential.get_token("https://cognitiveservices.azure.com/.default")
            
            self._client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token=token.token,
                api_version=app_settings.azure_openai.api_version,
            )
        return self._client
    
    async def run(self, user_message: str, context: Optional[str] = None) -> dict:
        """
        Run the agent with a user message.
        
        Args:
            user_message: The user's input
            context: Optional additional context
        
        Returns:
            dict with 'content' and 'agent_name' keys
        """
        client = await self._get_client()
        
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.instructions},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=app_settings.azure_openai.temperature,
                max_tokens=app_settings.azure_openai.max_tokens,
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "agent_name": self.name,
                "is_final": True,
            }
        
        except Exception as e:
            logger.exception(f"Error in agent {self.name}: {e}")
            return {
                "content": f"Error: {str(e)}",
                "agent_name": self.name,
                "is_final": True,
            }
    
    async def run_stream(self, user_message: str, context: Optional[str] = None):
        """
        Stream the agent response.
        
        Yields chunks of the response as they arrive.
        """
        client = await self._get_client()
        
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.instructions},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=app_settings.azure_openai.temperature,
                max_tokens=app_settings.azure_openai.max_tokens,
                stream=True,
            )
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield {
                        "content": content,
                        "agent_name": self.name,
                        "is_final": False,
                    }
            
            # Final message with complete content
            yield {
                "content": full_content,
                "agent_name": self.name,
                "is_final": True,
            }
        
        except Exception as e:
            logger.exception(f"Error in agent {self.name}: {e}")
            yield {
                "content": f"Error: {str(e)}",
                "agent_name": self.name,
                "is_final": True,
            }


class AgentRegistry:
    """Registry for managing agent instances."""
    
    _agents: dict = {}
    
    @classmethod
    def register(cls, name: str, agent: SimpleAgent) -> None:
        """Register an agent."""
        cls._agents[name] = agent
    
    @classmethod
    def get(cls, name: str) -> Optional[SimpleAgent]:
        """Get an agent by name."""
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names."""
        return list(cls._agents.keys())
