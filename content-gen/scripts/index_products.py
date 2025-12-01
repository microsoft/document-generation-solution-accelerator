"""
Index CosmosDB Products into Azure AI Search.

This script reads products from CosmosDB and indexes them into Azure AI Search
for use in grounding AI content generation.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "https://search-contentgen-jh.search.windows.net")
SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_PRODUCTS_INDEX", "products")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_AI_SEARCH_ADMIN_KEY", "")


def create_products_index(index_client: SearchIndexClient) -> SearchIndex:
    """Create the search index schema for products."""
    
    fields = [
        # Key field - use SKU as unique identifier
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True
        ),
        # Product identification
        SearchableField(
            name="product_name",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True
        ),
        SearchableField(
            name="sku",
            type=SearchFieldDataType.String,
            filterable=True
        ),
        SearchableField(
            name="model",
            type=SearchFieldDataType.String,
            filterable=True
        ),
        # Categories
        SearchableField(
            name="category",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True
        ),
        SearchableField(
            name="sub_category",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True
        ),
        # Descriptions
        SearchableField(
            name="marketing_description",
            type=SearchFieldDataType.String
        ),
        SearchableField(
            name="detailed_spec_description",
            type=SearchFieldDataType.String
        ),
        SearchableField(
            name="image_description",
            type=SearchFieldDataType.String
        ),
        # Combined text for search
        SearchableField(
            name="combined_text",
            type=SearchFieldDataType.String
        ),
        # Vector field for semantic search (optional - requires embedding model)
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="product-vector-profile"
        )
    ]
    
    # Configure vector search
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-algorithm"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="product-vector-profile",
                algorithm_configuration_name="hnsw-algorithm"
            )
        ]
    )
    
    # Configure semantic search
    semantic_config = SemanticConfiguration(
        name="product-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="product_name"),
            content_fields=[
                SemanticField(field_name="marketing_description"),
                SemanticField(field_name="detailed_spec_description"),
                SemanticField(field_name="image_description"),
                SemanticField(field_name="combined_text")
            ],
            keywords_fields=[
                SemanticField(field_name="category"),
                SemanticField(field_name="sub_category"),
                SemanticField(field_name="sku")
            ]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Create the index
    index = SearchIndex(
        name=SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    return index


def prepare_product_document(product: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a product document for indexing."""
    
    # Create combined text for search
    combined_text = f"""
    {product.get('product_name', '')}
    Category: {product.get('category', '')} - {product.get('sub_category', '')}
    SKU: {product.get('sku', '')} | Model: {product.get('model', '')}
    
    Marketing: {product.get('marketing_description', '')}
    
    Specifications: {product.get('detailed_spec_description', '')}
    
    Visual: {product.get('image_description', '')}
    """
    
    # Create document ID from SKU
    doc_id = product.get('sku', '').lower().replace("-", "_").replace(" ", "_")
    if not doc_id:
        doc_id = product.get('id', 'unknown')
    
    return {
        "id": doc_id,
        "product_name": product.get("product_name", ""),
        "sku": product.get("sku", ""),
        "model": product.get("model", ""),
        "category": product.get("category", ""),
        "sub_category": product.get("sub_category", ""),
        "marketing_description": product.get("marketing_description", ""),
        "detailed_spec_description": product.get("detailed_spec_description", ""),
        "image_description": product.get("image_description", ""),
        "combined_text": combined_text.strip(),
        "content_vector": [0.0] * 1536  # Placeholder - would need embedding model
    }


async def get_products_from_cosmos() -> List[Dict[str, Any]]:
    """Fetch all products from CosmosDB."""
    from backend.services.cosmos_service import get_cosmos_service
    
    cosmos_service = await get_cosmos_service()
    products = await cosmos_service.get_all_products()
    
    return [p.model_dump() for p in products]


async def index_products(search_client: SearchClient, products: List[Dict[str, Any]]) -> tuple:
    """Index products into the search index."""
    
    documents = []
    
    for product in products:
        doc = prepare_product_document(product)
        documents.append(doc)
        print(f"  ✓ Prepared: {product.get('product_name', 'Unknown')} ({product.get('sku', 'N/A')})")
    
    # Upload documents to the index
    result = search_client.upload_documents(documents)
    
    succeeded = sum(1 for r in result if r.succeeded)
    failed = sum(1 for r in result if not r.succeeded)
    
    return succeeded, failed


def get_search_credential():
    """Get search credential - prefer RBAC, fall back to API key."""
    try:
        credential = DefaultAzureCredential()
        # Test the credential
        test_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)
        list(test_client.list_indexes())
        print("Using RBAC authentication for search")
        return credential
    except Exception:
        if AZURE_SEARCH_ADMIN_KEY:
            print("Using API key authentication for search")
            return AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
        raise


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Index CosmosDB Products into Azure AI Search")
    print("=" * 60)
    print()
    
    search_credential = get_search_credential()
    
    # Create index client
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=search_credential
    )
    
    # Create or update the index
    print(f"Creating/updating search index: {SEARCH_INDEX_NAME}")
    print(f"Search endpoint: {SEARCH_ENDPOINT}")
    print()
    
    try:
        index = create_products_index(index_client)
        result = index_client.create_or_update_index(index)
        print(f"✓ Index '{result.name}' created/updated successfully")
    except Exception as e:
        print(f"✗ Failed to create index: {e}")
        raise
    
    # Get products from CosmosDB
    print()
    print("Fetching products from CosmosDB...")
    
    try:
        products = await get_products_from_cosmos()
        print(f"Found {len(products)} products in CosmosDB")
    except Exception as e:
        print(f"✗ Failed to fetch products from CosmosDB: {e}")
        raise
    
    if not products:
        print("No products found in CosmosDB. Run load_sample_data.py first.")
        return
    
    # Index the products
    print()
    print("Indexing products...")
    print("-" * 50)
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=search_credential
    )
    
    try:
        succeeded, failed = await index_products(search_client, products)
        print("-" * 50)
        print(f"\n✓ Indexed {succeeded} products successfully")
        if failed > 0:
            print(f"✗ Failed to index {failed} products")
    except Exception as e:
        print(f"✗ Failed to index products: {e}")
        raise
    
    # Summary
    print()
    print("=" * 60)
    print("Product Indexing Complete!")
    print("=" * 60)
    print(f"Index name: {SEARCH_INDEX_NAME}")
    print(f"Endpoint: {SEARCH_ENDPOINT}")
    print(f"Documents indexed: {succeeded}")
    print()
    print("Example search queries:")
    print("  - Search by category: 'electronics', 'footwear'")
    print("  - Search by product: 'wireless headphones', 'yoga mat'")
    print("  - Search by feature: 'noise cancellation', 'titanium'")


if __name__ == "__main__":
    asyncio.run(main())
