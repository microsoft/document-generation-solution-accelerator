"""
Sample data loader for Content Generation Solution Accelerator.

This script loads sample product data (Contoso Paints Catalog) into CosmosDB.
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.services.cosmos_service import get_cosmos_service
from backend.models import Product


# Contoso Paints Catalog - Paint colors with descriptions, tags, and prices
# Image URLs map to the uploaded PNG files in Azure Blob Storage
STORAGE_ACCOUNT = os.getenv("AZURE_BLOB_ACCOUNT_NAME", "storagecontentgenjh")
CONTAINER_NAME = os.getenv("AZURE_BLOB_PRODUCT_IMAGES_CONTAINER", "product-images")
IMAGE_BASE_URL = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net/{CONTAINER_NAME}"

SAMPLE_PRODUCTS = [
    {
        "product_name": "Snow Veil",
        "description": "A crisp white with a hint of warmth — perfect for open, modern interiors.",
        "tags": "soft white, airy, minimal, fresh",
        "price": 59.95,
        "sku": "CP-0001",
        "image_url": f"{IMAGE_BASE_URL}/SnowVeil.png"
    },
    {
        "product_name": "Porcelain Mist",
        "description": "A gentle off-white that softens spaces with a cozy, inviting glow.",
        "tags": "warm neutral, beige, cozy, calm",
        "price": 59.95,
        "sku": "CP-0002",
        "image_url": f"{IMAGE_BASE_URL}/PorcelainMist.png"
    },
    {
        "product_name": "Stone Dusk",
        "description": "A balanced mix of gray and beige, ideal for grounding a room without heaviness.",
        "tags": "greige, muted, balanced, modern",
        "price": 59.95,
        "sku": "CP-0003",
        "image_url": f"{IMAGE_BASE_URL}/StoneDusk.png"
    },
    {
        "product_name": "Fog Harbor",
        "description": "A moody gray with blue undertones that feels sleek and contemporary.",
        "tags": "cool gray, stormy, industrial, sleek",
        "price": 59.95,
        "sku": "CP-0004",
        "image_url": f"{IMAGE_BASE_URL}/FogHarbor.png"
    },
    {
        "product_name": "Graphite Fade",
        "description": "A dark graphite shade that adds weight and sophistication to feature walls.",
        "tags": "charcoal, deep gray, moody, bold",
        "price": 59.95,
        "sku": "CP-0005",
        "image_url": f"{IMAGE_BASE_URL}/GraphiteFade.png"
    },
    {
        "product_name": "Obsidian Pearl",
        "description": "A rich black that creates contrast and drama while staying refined.",
        "tags": "black, matte, dramatic, luxe",
        "price": 59.95,
        "sku": "CP-0006",
        "image_url": f"{IMAGE_BASE_URL}/ObsidianPearl.png"
    },
    {
        "product_name": "Steel Sky",
        "description": "A mid-tone slate blue that feels steady, grounded, and architectural.",
        "tags": "slate, bluish gray, urban, cool",
        "price": 59.95,
        "sku": "CP-0007",
        "image_url": f"{IMAGE_BASE_URL}/SteelSky.png"
    },
    {
        "product_name": "Blue Ash",
        "description": "A softened navy with gray undertones — stylish but not overpowering.",
        "tags": "midnight, muted navy, grounding, refined",
        "price": 59.95,
        "sku": "CP-0008",
        "image_url": f"{IMAGE_BASE_URL}/BlueAsh.png"
    },
    {
        "product_name": "Cloud Drift",
        "description": "A breezy pastel blue that brings calm and a sense of open sky.",
        "tags": "pale blue, soft, tranquil, airy",
        "price": 59.95,
        "sku": "CP-0009",
        "image_url": f"{IMAGE_BASE_URL}/CloudDrift.png"
    },
    {
        "product_name": "Silver Shore",
        "description": "A frosty gray with subtle silver hints — sharp, bright, and clean.",
        "tags": "cool gray, icy, clean, modern",
        "price": 59.95,
        "sku": "CP-0010",
        "image_url": f"{IMAGE_BASE_URL}/SilverShore.png"
    },
    {
        "product_name": "Seafoam Light",
        "description": "A soft seafoam tone that feels breezy and coastal without being too bold.",
        "tags": "pale green, misty, fresh, coastal",
        "price": 59.95,
        "sku": "CP-0011",
        "image_url": f"{IMAGE_BASE_URL}/SeafoamLight.png"
    },
    {
        "product_name": "Quiet Moss",
        "description": "A sage-infused gray that adds organic calm to any interior palette.",
        "tags": "sage gray, organic, muted, grounding",
        "price": 59.95,
        "sku": "CP-0012",
        "image_url": f"{IMAGE_BASE_URL}/QuietMoss.png"
    },
    {
        "product_name": "Olive Stone",
        "description": "A grounded olive shade that pairs well with natural textures like wood and linen.",
        "tags": "earthy, muted green, natural, rustic",
        "price": 59.95,
        "sku": "CP-0013",
        "image_url": f"{IMAGE_BASE_URL}/OliveStone.png"
    },
    {
        "product_name": "Verdant Haze",
        "description": "A muted teal that blends serenity with just enough depth for modern accents.",
        "tags": "soft teal, subdued, calming, serene",
        "price": 59.95,
        "sku": "CP-0014",
        "image_url": f"{IMAGE_BASE_URL}/VerdantHaze.png"
    },
    {
        "product_name": "Glacier Tint",
        "description": "A barely-there aqua that brings a refreshing, clean lift to light spaces.",
        "tags": "pale aqua, refreshing, crisp, airy",
        "price": 59.95,
        "sku": "CP-0015",
        "image_url": f"{IMAGE_BASE_URL}/GlacierTint.png"
    },
    {
        "product_name": "Pine Shadow",
        "description": "A forest-tinged gray with a natural edge, anchoring without feeling heavy.",
        "tags": "forest gray, cool green, earthy, grounding",
        "price": 59.95,
        "sku": "CP-0016",
        "image_url": f"{IMAGE_BASE_URL}/PineShadow.png"
    },
]


async def delete_existing_products():
    """Delete all existing products from CosmosDB."""
    print("Deleting existing products...")
    
    cosmos_service = await get_cosmos_service()
    deleted_count = await cosmos_service.delete_all_products()
    
    print(f"  ✓ Deleted {deleted_count} existing products.")
    return deleted_count


async def load_sample_data():
    """Load sample products into CosmosDB."""
    print("\nLoading Contoso Paints Catalog...")
    
    cosmos_service = await get_cosmos_service()
    
    loaded_count = 0
    for product_data in SAMPLE_PRODUCTS:
        try:
            product = Product(**product_data)
            await cosmos_service.upsert_product(product)
            print(f"  ✓ Loaded: {product.product_name} ({product.sku})")
            loaded_count += 1
        except Exception as e:
            print(f"  ✗ Failed to load {product_data.get('product_name', 'unknown')}: {e}")
    
    print(f"\nLoaded {loaded_count} products from Contoso Paints Catalog.")


async def main():
    """Main entry point."""
    try:
        # Delete existing products first
        await delete_existing_products()
        
        # Load new products
        await load_sample_data()
    except Exception as e:
        print(f"Error loading sample data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
