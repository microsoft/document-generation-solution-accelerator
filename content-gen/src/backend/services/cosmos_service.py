"""
CosmosDB Service - Manages products and conversation storage.

Provides async operations for:
- Product catalog (CRUD operations)
- Conversation history
- Creative brief storage
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone

from azure.cosmos.aio import CosmosClient, ContainerProxy
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential

from settings import app_settings
from models import Product, CreativeBrief

logger = logging.getLogger(__name__)


class CosmosDBService:
    """Service for interacting with Azure Cosmos DB."""
    
    def __init__(self):
        self._client: Optional[CosmosClient] = None
        self._products_container: Optional[ContainerProxy] = None
        self._conversations_container: Optional[ContainerProxy] = None
    
    async def _get_credential(self):
        """Get Azure credential for authentication."""
        client_id = app_settings.base_settings.azure_client_id
        if client_id:
            return ManagedIdentityCredential(client_id=client_id)
        return DefaultAzureCredential()
    
    async def initialize(self) -> None:
        """Initialize CosmosDB client and containers."""
        if self._client:
            return
        
        credential = await self._get_credential()
        
        self._client = CosmosClient(
            url=app_settings.cosmos.endpoint,
            credential=credential
        )
        
        database = self._client.get_database_client(
            app_settings.cosmos.database_name
        )
        
        self._products_container = database.get_container_client(
            app_settings.cosmos.products_container
        )
        
        self._conversations_container = database.get_container_client(
            app_settings.cosmos.conversations_container
        )
        
        logger.info("CosmosDB service initialized")
    
    async def close(self) -> None:
        """Close the CosmosDB client."""
        if self._client:
            await self._client.close()
            self._client = None
    
    # ==================== Product Operations ====================
    
    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Retrieve a product by its SKU.
        
        Args:
            sku: Product SKU identifier
        
        Returns:
            Product if found, None otherwise
        """
        await self.initialize()
        
        query = "SELECT * FROM c WHERE c.sku = @sku"
        params = [{"name": "@sku", "value": sku}]
        
        items = []
        async for item in self._products_container.query_items(
            query=query,
            parameters=params
        ):
            items.append(item)
        
        if items:
            return Product(**items[0])
        return None
    
    async def get_products_by_category(
        self,
        category: str,
        sub_category: Optional[str] = None,
        limit: int = 10
    ) -> List[Product]:
        """
        Retrieve products by category.
        
        Args:
            category: Product category
            sub_category: Optional sub-category filter
            limit: Maximum number of products to return
        
        Returns:
            List of matching products
        """
        await self.initialize()
        
        if sub_category:
            query = """
                SELECT TOP @limit * FROM c 
                WHERE c.category = @category AND c.sub_category = @sub_category
            """
            params = [
                {"name": "@category", "value": category},
                {"name": "@sub_category", "value": sub_category},
                {"name": "@limit", "value": limit}
            ]
        else:
            query = "SELECT TOP @limit * FROM c WHERE c.category = @category"
            params = [
                {"name": "@category", "value": category},
                {"name": "@limit", "value": limit}
            ]
        
        products = []
        async for item in self._products_container.query_items(
            query=query,
            parameters=params
        ):
            products.append(Product(**item))
        
        return products
    
    async def search_products(
        self,
        search_term: str,
        limit: int = 10
    ) -> List[Product]:
        """
        Search products by name or description.
        
        Args:
            search_term: Text to search for
            limit: Maximum number of products to return
        
        Returns:
            List of matching products
        """
        await self.initialize()
        
        search_lower = search_term.lower()
        query = """
            SELECT TOP @limit * FROM c 
            WHERE CONTAINS(LOWER(c.product_name), @search) 
               OR CONTAINS(LOWER(c.marketing_description), @search)
               OR CONTAINS(LOWER(c.detailed_spec_description), @search)
        """
        params = [
            {"name": "@search", "value": search_lower},
            {"name": "@limit", "value": limit}
        ]
        
        products = []
        async for item in self._products_container.query_items(
            query=query,
            parameters=params
        ):
            products.append(Product(**item))
        
        return products
    
    async def upsert_product(self, product: Product) -> Product:
        """
        Create or update a product.
        
        Args:
            product: Product to upsert
        
        Returns:
            The upserted product
        """
        await self.initialize()
        
        item = product.model_dump()
        item["id"] = product.sku  # Use SKU as document ID
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await self._products_container.upsert_item(item)
        return Product(**result)
    
    async def delete_product(self, sku: str) -> bool:
        """
        Delete a product by SKU.
        
        Args:
            sku: Product SKU (also used as document ID)
        
        Returns:
            True if deleted successfully
        """
        await self.initialize()
        
        try:
            await self._products_container.delete_item(
                item=sku,
                partition_key=sku
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to delete product {sku}: {e}")
            return False
    
    async def delete_all_products(self) -> int:
        """
        Delete all products from the container.
        
        Returns:
            Number of products deleted
        """
        await self.initialize()
        
        deleted_count = 0
        query = "SELECT c.id FROM c"
        
        async for item in self._products_container.query_items(query=query):
            try:
                await self._products_container.delete_item(
                    item=item["id"],
                    partition_key=item["id"]
                )
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete product {item['id']}: {e}")
        
        return deleted_count
    
    async def get_all_products(self, limit: int = 100) -> List[Product]:
        """
        Retrieve all products.
        
        Args:
            limit: Maximum number of products to return
        
        Returns:
            List of all products
        """
        await self.initialize()
        
        query = "SELECT TOP @limit * FROM c"
        params = [{"name": "@limit", "value": limit}]
        
        products = []
        async for item in self._products_container.query_items(
            query=query,
            parameters=params
        ):
            products.append(Product(**item))
        
        return products
    
    # ==================== Conversation Operations ====================
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Optional[dict]:
        """
        Retrieve a conversation by ID.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for partition key (may not match if conversation was created by different user)
        
        Returns:
            Conversation data if found
        """
        await self.initialize()
        
        try:
            # First try direct read with provided user_id (fast path)
            item = await self._conversations_container.read_item(
                item=conversation_id,
                partition_key=user_id
            )
            return item
        except Exception:
            pass
        
        # Fallback: cross-partition query to find conversation by ID
        # This handles cases where the conversation was created with a different user_id
        try:
            query = "SELECT * FROM c WHERE c.id = @id"
            params = [{"name": "@id", "value": conversation_id}]
            
            async for item in self._conversations_container.query_items(
                query=query,
                parameters=params,
                max_item_count=1
            ):
                return item
        except Exception:
            pass
        
        return None
    
    async def save_conversation(
        self,
        conversation_id: str,
        user_id: str,
        messages: List[dict],
        brief: Optional[CreativeBrief] = None,
        metadata: Optional[dict] = None,
        generated_content: Optional[dict] = None
    ) -> dict:
        """
        Save or update a conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for partition key
            messages: List of conversation messages
            brief: Associated creative brief
            metadata: Additional metadata
            generated_content: Generated marketing content
        
        Returns:
            The saved conversation document
        """
        await self.initialize()
        
        item = {
            "id": conversation_id,
            "user_id": user_id,
            "messages": messages,
            "brief": brief.model_dump() if brief else None,
            "metadata": metadata or {},
            "generated_content": generated_content,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await self._conversations_container.upsert_item(item)
        return result
    
    async def save_generated_content(
        self,
        conversation_id: str,
        user_id: str,
        generated_content: dict
    ) -> dict:
        """
        Save generated content to an existing conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for partition key
            generated_content: The generated content to save
        
        Returns:
            Updated conversation document
        """
        await self.initialize()
        
        conversation = await self.get_conversation(conversation_id, user_id)
        
        if conversation:
            conversation["generated_content"] = generated_content
            conversation["updated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            conversation = {
                "id": conversation_id,
                "user_id": user_id,
                "messages": [],
                "generated_content": generated_content,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        result = await self._conversations_container.upsert_item(conversation)
        return result
    
    async def add_message_to_conversation(
        self,
        conversation_id: str,
        user_id: str,
        message: dict
    ) -> dict:
        """
        Add a message to an existing conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for partition key
            message: Message to add
        
        Returns:
            Updated conversation document
        """
        await self.initialize()
        
        conversation = await self.get_conversation(conversation_id, user_id)
        
        if conversation:
            conversation["messages"].append(message)
            conversation["updated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            conversation = {
                "id": conversation_id,
                "user_id": user_id,
                "messages": [message],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        result = await self._conversations_container.upsert_item(conversation)
        return result
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[dict]:
        """
        Get all conversations for a user with summary data.
        
        Args:
            user_id: User ID ("anonymous" for unauthenticated users)
            limit: Maximum number of conversations
        
        Returns:
            List of conversation summaries
        """
        await self.initialize()
        
        # For anonymous users, also include conversations with empty/null/undefined user_id
        # This handles legacy data before "anonymous" was used as the default
        if user_id == "anonymous":
            query = """
                SELECT TOP @limit c.id, c.user_id, c.updated_at, c.messages, c.brief
                FROM c 
                WHERE c.user_id = @user_id 
                   OR c.user_id = "" 
                   OR c.user_id = null 
                   OR NOT IS_DEFINED(c.user_id)
                ORDER BY c.updated_at DESC
            """
            params = [
                {"name": "@user_id", "value": user_id},
                {"name": "@limit", "value": limit}
            ]
        else:
            # For authenticated users, only show their conversations
            query = """
                SELECT TOP @limit c.id, c.user_id, c.updated_at, c.messages, c.brief
                FROM c 
                WHERE c.user_id = @user_id
                ORDER BY c.updated_at DESC
            """
            params = [
                {"name": "@user_id", "value": user_id},
                {"name": "@limit", "value": limit}
            ]
        
        conversations = []
        async for item in self._conversations_container.query_items(
            query=query,
            parameters=params
        ):
            messages = item.get("messages", [])
            brief = item.get("brief", {})
            
            # Extract title from brief overview or first user message
            title = "Untitled Conversation"
            if brief and brief.get("overview"):
                title = brief["overview"][:50]
            elif messages:
                for msg in messages:
                    if msg.get("role") == "user":
                        title = msg.get("content", "")[:50]
                        break
            
            # Get last message preview
            last_message = ""
            if messages:
                last_msg = messages[-1]
                last_message = last_msg.get("content", "")[:100]
            
            conversations.append({
                "id": item["id"],
                "title": title,
                "lastMessage": last_message,
                "timestamp": item.get("updated_at", ""),
                "messageCount": len(messages)
            })
        
        return conversations
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for partition key
        
        Returns:
            True if deleted successfully
        """
        await self.initialize()
        
        try:
            # First try to delete with provided user_id
            await self._conversations_container.delete_item(
                item=conversation_id,
                partition_key=user_id
            )
            return True
        except Exception:
            pass
        
        # Fallback: find the conversation first to get the correct partition key
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if conversation:
                actual_user_id = conversation.get("user_id", "")
                await self._conversations_container.delete_item(
                    item=conversation_id,
                    partition_key=actual_user_id
                )
                return True
        except Exception as e:
            logger.warning(f"Failed to delete conversation {conversation_id}: {e}")
            raise
        
        return False


# Singleton instance
_cosmos_service: Optional[CosmosDBService] = None


async def get_cosmos_service() -> CosmosDBService:
    """Get or create the singleton CosmosDB service instance."""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosDBService()
        await _cosmos_service.initialize()
    return _cosmos_service
