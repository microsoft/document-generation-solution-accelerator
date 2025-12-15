#!/usr/bin/env python3
"""
Post-Deployment Script for Content Generation Solution Accelerator.

This unified script handles all post-deployment tasks:
1. Enable public access on Azure resources (for data ingestion)
2. Upload product images to Azure Blob Storage
3. Load sample product data to CosmosDB
4. Create and populate Azure AI Search index
5. Disable public access on Azure resources (restore security)
6. Run application health tests

Usage:
    python post_deploy.py --resource-group rg-name [options]

Options:
    --resource-group, -g    Resource group name (required)
    --app-name              App Service name (auto-detected if not provided)
    --skip-images           Skip uploading images
    --skip-data             Skip loading sample data
    --skip-index            Skip creating search index
    --skip-tests            Skip application tests
    --skip-descriptions     Skip generating AI image descriptions
    --keep-public-access    Don't disable public access after completion
    --dry-run               Show what would be done without executing
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

import httpx
from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField, VectorSearch,
    VectorSearchProfile, HnswAlgorithmConfiguration,
    SemanticConfiguration, SemanticField,
    SemanticPrioritizedFields, SemanticSearch,
)
from azure.core.credentials import AzureKeyCredential

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@dataclass
class ResourceConfig:
    """Configuration for Azure resources."""
    resource_group: str
    storage_account: str
    cosmos_account: str
    search_service: str
    app_service: str
    container_name: str = "product-images"
    database_name: str = "content_generation_db"
    search_index: str = "products"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")


def print_step(text: str):
    """Print a step indicator."""
    print(f"{Colors.BLUE}→ {text}{Colors.END}")


def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def run_az_command(args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run an Azure CLI command."""
    cmd = ["az"] + args
    return subprocess.run(cmd, capture_output=capture_output, text=True)


def discover_resources(resource_group: str, app_name: Optional[str] = None) -> ResourceConfig:
    """Discover Azure resources in the resource group."""
    print_step("Discovering Azure resources...")
    
    # Get storage account
    result = run_az_command([
        "storage", "account", "list",
        "--resource-group", resource_group,
        "--query", "[0].name", "-o", "tsv"
    ])
    storage_account = result.stdout.strip()
    
    # Get Cosmos DB account
    result = run_az_command([
        "cosmosdb", "list",
        "--resource-group", resource_group,
        "--query", "[0].name", "-o", "tsv"
    ])
    cosmos_account = result.stdout.strip()
    
    # Get AI Search service
    result = run_az_command([
        "search", "service", "list",
        "--resource-group", resource_group,
        "--query", "[0].name", "-o", "tsv"
    ])
    search_service = result.stdout.strip()
    
    # Get App Service (or use provided name)
    if not app_name:
        result = run_az_command([
            "webapp", "list",
            "--resource-group", resource_group,
            "--query", "[0].name", "-o", "tsv"
        ])
        app_name = result.stdout.strip()
    
    config = ResourceConfig(
        resource_group=resource_group,
        storage_account=storage_account,
        cosmos_account=cosmos_account,
        search_service=search_service,
        app_service=app_name
    )
    
    print(f"  Storage Account: {config.storage_account}")
    print(f"  Cosmos DB:       {config.cosmos_account}")
    print(f"  AI Search:       {config.search_service}")
    print(f"  App Service:     {config.app_service}")
    
    return config


def set_public_access(config: ResourceConfig, enabled: bool, dry_run: bool = False):
    """Enable or disable public network access on resources."""
    state = "Enabled" if enabled else "Disabled"
    action = "Enabling" if enabled else "Disabling"
    print_header(f"{action} Public Network Access")
    
    if dry_run:
        print_warning(f"DRY RUN: Would set public access to {state}")
        return
    
    # Storage Account
    print_step(f"Storage Account: {config.storage_account}")
    result = run_az_command([
        "storage", "account", "update",
        "--name", config.storage_account,
        "--resource-group", config.resource_group,
        "--public-network-access", state,
        "-o", "none"
    ])
    if result.returncode == 0:
        print_success(f"Public access {state.lower()}")
    else:
        print_error(f"Failed: {result.stderr}")
    
    # Cosmos DB
    print_step(f"Cosmos DB: {config.cosmos_account}")
    cosmos_state = "ENABLED" if enabled else "DISABLED"
    result = run_az_command([
        "cosmosdb", "update",
        "--name", config.cosmos_account,
        "--resource-group", config.resource_group,
        "--public-network-access", cosmos_state,
        "-o", "none"
    ])
    if result.returncode == 0:
        print_success(f"Public access {state.lower()}")
    else:
        print_error(f"Failed: {result.stderr}")
    
    # AI Search
    print_step(f"AI Search: {config.search_service}")
    search_state = "enabled" if enabled else "disabled"
    result = run_az_command([
        "search", "service", "update",
        "--name", config.search_service,
        "--resource-group", config.resource_group,
        "--public-access", search_state,
        "-o", "none"
    ])
    if result.returncode == 0:
        print_success(f"Public access {state.lower()}")
    else:
        print_error(f"Failed: {result.stderr}")
    
    if enabled:
        print_warning("Waiting 10 seconds for access changes to propagate...")
        time.sleep(10)


async def upload_images(config: ResourceConfig, dry_run: bool = False) -> int:
    """Upload product images to Azure Blob Storage."""
    print_header("Uploading Product Images")
    
    images_folder = Path(__file__).parent / "images"
    if not images_folder.exists():
        print_error(f"Images folder not found: {images_folder}")
        return 0
    
    image_files = (
        list(images_folder.glob("*.jpg")) +
        list(images_folder.glob("*.JPG")) +
        list(images_folder.glob("*.png")) +
        list(images_folder.glob("*.PNG"))
    )
    
    if not image_files:
        print_warning("No image files found")
        return 0
    
    print(f"Found {len(image_files)} image files")
    
    if dry_run:
        print_warning("DRY RUN: Would upload images to blob storage")
        for img in sorted(image_files):
            print(f"  - {img.name}")
        return len(image_files)
    
    account_url = f"https://{config.storage_account}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    
    uploaded = 0
    async with BlobServiceClient(account_url=account_url, credential=credential) as blob_service:
        container_client = blob_service.get_container_client(config.container_name)
        
        # Create container if needed
        try:
            await container_client.create_container()
            print_success(f"Created container: {config.container_name}")
        except Exception as e:
            if "ContainerAlreadyExists" not in str(e):
                print_warning(f"Container note: {e}")
        
        for image_path in sorted(image_files):
            blob_name = image_path.name
            content_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
            
            try:
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                blob_client = container_client.get_blob_client(blob_name)
                await blob_client.upload_blob(
                    image_data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=content_type)
                )
                print_success(f"{blob_name} ({len(image_data):,} bytes)")
                uploaded += 1
            except Exception as e:
                print_error(f"Failed to upload {blob_name}: {e}")
    
    print(f"\nUploaded {uploaded}/{len(image_files)} images")
    return uploaded


async def load_sample_data(config: ResourceConfig, generate_descriptions: bool = True, dry_run: bool = False) -> int:
    """Load sample product data into CosmosDB."""
    print_header("Loading Sample Product Data")
    
    # Import here to avoid circular imports
    from backend.services.cosmos_service import get_cosmos_service
    from backend.models import Product
    
    # Sample products (Contoso Paints)
    image_base_url = f"https://{config.storage_account}.blob.core.windows.net/{config.container_name}"
    
    sample_products = [
        {"product_name": "Snow Veil", "description": "A crisp white with a hint of warmth — perfect for open, modern interiors.", "tags": "soft white, airy, minimal, fresh", "price": 59.95, "sku": "CP-0001", "image_url": f"{image_base_url}/SnowVeil.png", "category": "Paint"},
        {"product_name": "Porcelain Mist", "description": "A gentle off-white that softens spaces with a cozy, inviting glow.", "tags": "warm neutral, beige, cozy, calm", "price": 59.95, "sku": "CP-0002", "image_url": f"{image_base_url}/PorcelainMist.png", "category": "Paint"},
        {"product_name": "Stone Dusk", "description": "A balanced mix of gray and beige, ideal for grounding a room without heaviness.", "tags": "greige, muted, balanced, modern", "price": 59.95, "sku": "CP-0003", "image_url": f"{image_base_url}/StoneDusk.png", "category": "Paint"},
        {"product_name": "Fog Harbor", "description": "A moody gray with blue undertones that feels sleek and contemporary.", "tags": "cool gray, stormy, industrial, sleek", "price": 59.95, "sku": "CP-0004", "image_url": f"{image_base_url}/FogHarbor.png", "category": "Paint"},
        {"product_name": "Graphite Fade", "description": "A dark graphite shade that adds weight and sophistication to feature walls.", "tags": "charcoal, deep gray, moody, bold", "price": 59.95, "sku": "CP-0005", "image_url": f"{image_base_url}/GraphiteFade.png", "category": "Paint"},
        {"product_name": "Obsidian Pearl", "description": "A rich black that creates contrast and drama while staying refined.", "tags": "black, matte, dramatic, luxe", "price": 59.95, "sku": "CP-0006", "image_url": f"{image_base_url}/ObsidianPearl.png", "category": "Paint"},
        {"product_name": "Steel Sky", "description": "A mid-tone slate blue that feels steady, grounded, and architectural.", "tags": "slate, bluish gray, urban, cool", "price": 59.95, "sku": "CP-0007", "image_url": f"{image_base_url}/SteelSky.png", "category": "Paint"},
        {"product_name": "Blue Ash", "description": "A softened navy with gray undertones — stylish but not overpowering.", "tags": "midnight, muted navy, grounding, refined", "price": 59.95, "sku": "CP-0008", "image_url": f"{image_base_url}/BlueAsh.png", "category": "Paint"},
        {"product_name": "Cloud Drift", "description": "A breezy pastel blue that brings calm and a sense of open sky.", "tags": "pale blue, soft, tranquil, airy", "price": 59.95, "sku": "CP-0009", "image_url": f"{image_base_url}/CloudDrift.png", "category": "Paint"},
        {"product_name": "Silver Shore", "description": "A frosty gray with subtle silver hints — sharp, bright, and clean.", "tags": "cool gray, icy, clean, modern", "price": 59.95, "sku": "CP-0010", "image_url": f"{image_base_url}/SilverShore.png", "category": "Paint"},
        {"product_name": "Seafoam Light", "description": "A soft seafoam tone that feels breezy and coastal without being too bold.", "tags": "pale green, misty, fresh, coastal", "price": 59.95, "sku": "CP-0011", "image_url": f"{image_base_url}/SeafoamLight.png", "category": "Paint"},
        {"product_name": "Quiet Moss", "description": "A sage-infused gray that adds organic calm to any interior palette.", "tags": "sage gray, organic, muted, grounding", "price": 59.95, "sku": "CP-0012", "image_url": f"{image_base_url}/QuietMoss.png", "category": "Paint"},
        {"product_name": "Olive Stone", "description": "A grounded olive shade that pairs well with natural textures like wood and linen.", "tags": "earthy, muted green, natural, rustic", "price": 59.95, "sku": "CP-0013", "image_url": f"{image_base_url}/OliveStone.png", "category": "Paint"},
        {"product_name": "Verdant Haze", "description": "A muted teal that blends serenity with just enough depth for modern accents.", "tags": "soft teal, subdued, calming, serene", "price": 59.95, "sku": "CP-0014", "image_url": f"{image_base_url}/VerdantHaze.png", "category": "Paint"},
        {"product_name": "Glacier Tint", "description": "A barely-there aqua that brings a refreshing, clean lift to light spaces.", "tags": "pale aqua, refreshing, crisp, airy", "price": 59.95, "sku": "CP-0015", "image_url": f"{image_base_url}/GlacierTint.png", "category": "Paint"},
        {"product_name": "Pine Shadow", "description": "A forest-tinged gray with a natural edge, anchoring without feeling heavy.", "tags": "forest gray, cool green, earthy, grounding", "price": 59.95, "sku": "CP-0016", "image_url": f"{image_base_url}/PineShadow.png", "category": "Paint"},
    ]
    
    print(f"Sample products: {len(sample_products)} Contoso Paints items")
    
    if dry_run:
        print_warning("DRY RUN: Would load products to CosmosDB")
        for p in sample_products:
            print(f"  - {p['product_name']} ({p['sku']})")
        return len(sample_products)
    
    cosmos_service = await get_cosmos_service()
    
    # Delete existing products
    print_step("Deleting existing products...")
    deleted = await cosmos_service.delete_all_products()
    print(f"  Deleted {deleted} existing products")
    
    # Load new products
    print_step("Loading products...")
    loaded = 0
    for product_data in sample_products:
        try:
            product = Product(**product_data)
            await cosmos_service.upsert_product(product)
            print_success(f"{product.product_name} ({product.sku})")
            loaded += 1
        except Exception as e:
            print_error(f"Failed to load {product_data['product_name']}: {e}")
    
    print(f"\nLoaded {loaded}/{len(sample_products)} products")
    return loaded


async def create_search_index(config: ResourceConfig, dry_run: bool = False) -> int:
    """Create and populate the Azure AI Search index."""
    print_header("Creating Search Index")
    
    from backend.services.cosmos_service import get_cosmos_service
    
    search_endpoint = f"https://{config.search_service}.search.windows.net"
    
    if dry_run:
        print_warning("DRY RUN: Would create search index and index products")
        return 0
    
    # Get search admin key (more reliable than RBAC for indexing)
    result = run_az_command([
        "search", "admin-key", "show",
        "--service-name", config.search_service,
        "--resource-group", config.resource_group,
        "--query", "primaryKey", "-o", "tsv"
    ])
    admin_key = result.stdout.strip()
    
    if admin_key:
        credential = AzureKeyCredential(admin_key)
        print_step("Using API key authentication")
    else:
        credential = DefaultAzureCredential()
        print_step("Using RBAC authentication")
    
    # Create index client
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    
    # Define index schema
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="product_name", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchableField(name="sku", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="model", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="sub_category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="marketing_description", type=SearchFieldDataType.String),
        SearchableField(name="detailed_spec_description", type=SearchFieldDataType.String),
        SearchableField(name="image_description", type=SearchFieldDataType.String),
        SearchableField(name="combined_text", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="product-vector-profile"
        )
    ]
    
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algorithm")],
        profiles=[VectorSearchProfile(name="product-vector-profile", algorithm_configuration_name="hnsw-algorithm")]
    )
    
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
    
    index = SearchIndex(
        name=config.search_index,
        fields=fields,
        vector_search=vector_search,
        semantic_search=SemanticSearch(configurations=[semantic_config])
    )
    
    # Create or update index
    print_step(f"Creating index: {config.search_index}")
    try:
        index_client.create_or_update_index(index)
        print_success("Index created/updated")
    except Exception as e:
        print_error(f"Failed to create index: {e}")
        return 0
    
    # Get products from CosmosDB
    print_step("Fetching products from CosmosDB...")
    cosmos_service = await get_cosmos_service()
    products = await cosmos_service.get_all_products()
    print(f"  Found {len(products)} products")
    
    if not products:
        print_warning("No products to index")
        return 0
    
    # Prepare documents
    print_step("Indexing products...")
    documents = []
    for product in products:
        p = product.model_dump()
        doc_id = p.get('sku', '').lower().replace("-", "_").replace(" ", "_") or p.get('id', 'unknown')
        
        combined_text = f"""
        {p.get('product_name', '')}
        Category: {p.get('category', '')} - {p.get('sub_category', '')}
        SKU: {p.get('sku', '')} | Model: {p.get('model', '')}
        Marketing: {p.get('marketing_description', '')}
        Specifications: {p.get('detailed_spec_description', '')}
        Visual: {p.get('image_description', '')}
        """
        
        documents.append({
            "id": doc_id,
            "product_name": p.get("product_name", ""),
            "sku": p.get("sku", ""),
            "model": p.get("model", ""),
            "category": p.get("category", ""),
            "sub_category": p.get("sub_category", ""),
            "marketing_description": p.get("marketing_description", ""),
            "detailed_spec_description": p.get("detailed_spec_description", ""),
            "image_description": p.get("image_description", ""),
            "combined_text": combined_text.strip(),
            "content_vector": [0.0] * 1536
        })
        print_success(f"{p.get('product_name', 'Unknown')} ({p.get('sku', 'N/A')})")
    
    # Upload documents
    search_client = SearchClient(endpoint=search_endpoint, index_name=config.search_index, credential=credential)
    
    try:
        result = search_client.upload_documents(documents)
        succeeded = sum(1 for r in result if r.succeeded)
        failed = sum(1 for r in result if not r.succeeded)
        print(f"\nIndexed {succeeded} products ({failed} failed)")
        return succeeded
    except Exception as e:
        print_error(f"Failed to index documents: {e}")
        return 0


async def run_application_tests(config: ResourceConfig, dry_run: bool = False) -> Dict[str, bool]:
    """Run application health tests."""
    print_header("Running Application Tests")
    
    if dry_run:
        print_warning("DRY RUN: Would run application tests")
        return {}
    
    # Get app URL
    result = run_az_command([
        "webapp", "show",
        "--name", config.app_service,
        "--resource-group", config.resource_group,
        "--query", "defaultHostName", "-o", "tsv"
    ])
    app_url = f"https://{result.stdout.strip()}"
    
    print(f"App URL: {app_url}")
    print()
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Frontend
        print_step("Testing Frontend (GET /)")
        try:
            response = await client.get(f"{app_url}/")
            if response.status_code == 200 and "<!DOCTYPE html>" in response.text:
                print_success("Frontend serving HTML")
                results["frontend"] = True
            else:
                print_error(f"Unexpected response: {response.status_code}")
                results["frontend"] = False
        except Exception as e:
            print_error(f"Failed: {e}")
            results["frontend"] = False
        
        # Test 2: Health endpoint
        print_step("Testing Health (GET /api/health)")
        try:
            response = await client.get(f"{app_url}/api/health")
            if response.status_code == 200:
                print_success(f"Health OK: {response.json()}")
                results["health"] = True
            else:
                print_warning(f"Health returned {response.status_code}")
                results["health"] = False
        except Exception as e:
            print_warning(f"Health check failed: {e}")
            results["health"] = False
        
        # Test 3: Brief Parsing (POST /api/brief/parse)
        print_step("Testing Brief Parsing (POST /api/brief/parse)")
        try:
            response = await client.post(
                f"{app_url}/api/brief/parse",
                json={"brief_text": "Create an ad for calm interior paint for homeowners."},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                if "brief" in data:
                    print_success(f"Brief parsed: {data['brief'].get('overview', '')[:60]}...")
                    results["brief_parse"] = True
                else:
                    print_error(f"Unexpected response: {data}")
                    results["brief_parse"] = False
            else:
                print_error(f"Failed: {response.status_code} - {response.text[:200]}")
                results["brief_parse"] = False
        except Exception as e:
            print_error(f"Failed: {e}")
            results["brief_parse"] = False
        
        # Test 4: Product Search (GET /api/products)
        print_step("Testing Product Search (GET /api/products?search=blue)")
        try:
            response = await client.get(f"{app_url}/api/products?search=blue&limit=3")
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                products = data.get("products", [])
                if count > 0:
                    print_success(f"Found {count} products: {[p['product_name'] for p in products]}")
                    results["product_search"] = True
                else:
                    print_warning("No products found (search index may need time)")
                    results["product_search"] = False
            else:
                print_error(f"Failed: {response.status_code}")
                results["product_search"] = False
        except Exception as e:
            print_error(f"Failed: {e}")
            results["product_search"] = False
        
        # Test 5: Product List (GET /api/products)
        print_step("Testing Product List (GET /api/products)")
        try:
            response = await client.get(f"{app_url}/api/products?limit=5")
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                print_success(f"Listed {count} products")
                results["product_list"] = True
            else:
                print_error(f"Failed: {response.status_code}")
                results["product_list"] = False
        except Exception as e:
            print_error(f"Failed: {e}")
            results["product_list"] = False
    
    # Summary
    print()
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print_success(f"All {total} tests passed!")
    else:
        print_warning(f"{passed}/{total} tests passed")
    
    return results


def print_summary(
    images_uploaded: int,
    products_loaded: int,
    products_indexed: int,
    test_results: Dict[str, bool]
):
    """Print final summary."""
    print_header("Post-Deployment Summary")
    
    print(f"  Images Uploaded:    {images_uploaded}")
    print(f"  Products Loaded:    {products_loaded}")
    print(f"  Products Indexed:   {products_indexed}")
    
    if test_results:
        print()
        print("  Application Tests:")
        for test, passed in test_results.items():
            status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
            print(f"    {test}: {status}")
    
    print()


async def main():
    parser = argparse.ArgumentParser(
        description="Post-deployment script for Content Generation Solution Accelerator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-g", "--resource-group", required=True, help="Azure resource group name")
    parser.add_argument("--app-name", help="App Service name (auto-detected if not provided)")
    parser.add_argument("--skip-images", action="store_true", help="Skip uploading images")
    parser.add_argument("--skip-data", action="store_true", help="Skip loading sample data")
    parser.add_argument("--skip-index", action="store_true", help="Skip creating search index")
    parser.add_argument("--skip-tests", action="store_true", help="Skip application tests")
    parser.add_argument("--skip-descriptions", action="store_true", help="Skip AI image descriptions")
    parser.add_argument("--keep-public-access", action="store_true", help="Keep public access enabled after completion")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    print_header("Content Generation Solution Accelerator - Post Deployment")
    print(f"Resource Group: {args.resource_group}")
    print(f"Dry Run: {args.dry_run}")
    print()
    
    # Discover resources
    config = discover_resources(args.resource_group, args.app_name)
    
    images_uploaded = 0
    products_loaded = 0
    products_indexed = 0
    test_results = {}
    
    try:
        # Enable public access
        set_public_access(config, enabled=True, dry_run=args.dry_run)
        
        # Upload images
        if not args.skip_images:
            images_uploaded = await upload_images(config, dry_run=args.dry_run)
        
        # Load sample data
        if not args.skip_data:
            products_loaded = await load_sample_data(
                config,
                generate_descriptions=not args.skip_descriptions,
                dry_run=args.dry_run
            )
        
        # Create search index
        if not args.skip_index:
            products_indexed = await create_search_index(config, dry_run=args.dry_run)
        
        # Disable public access (restore security)
        if not args.keep_public_access:
            set_public_access(config, enabled=False, dry_run=args.dry_run)
        
        # Run application tests
        if not args.skip_tests:
            test_results = await run_application_tests(config, dry_run=args.dry_run)
        
    except Exception as e:
        print_error(f"Error during post-deployment: {e}")
        
        # Try to disable public access even on error
        if not args.keep_public_access:
            print_warning("Attempting to disable public access...")
            set_public_access(config, enabled=False, dry_run=args.dry_run)
        
        raise
    
    # Print summary
    print_summary(images_uploaded, products_loaded, products_indexed, test_results)


if __name__ == "__main__":
    asyncio.run(main())
