"""
Sample data loader for Content Generation Solution Accelerator.

This script loads sample product data (Contoso Paints Catalog) into CosmosDB.
It also generates detailed image descriptions using GPT-4 Vision by analyzing
the product images stored in Azure Blob Storage.
"""

import asyncio
import base64
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob.aio import BlobServiceClient
from openai import AsyncAzureOpenAI

from backend.services.cosmos_service import get_cosmos_service
from backend.models import Product
from backend.settings import app_settings


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


async def get_openai_client():
    """Get an authenticated Azure OpenAI client."""
    client_id = app_settings.base_settings.azure_client_id
    if client_id:
        credential = ManagedIdentityCredential(client_id=client_id)
    else:
        credential = DefaultAzureCredential()
    
    token = await credential.get_token("https://cognitiveservices.azure.com/.default")
    
    client = AsyncAzureOpenAI(
        azure_endpoint=app_settings.azure_openai.endpoint,
        azure_ad_token=token.token,
        api_version=app_settings.azure_openai.api_version,
    )
    
    return client


async def get_image_from_blob(image_url: str) -> bytes:
    """Download an image from Azure Blob Storage."""
    # Try connection string first (from environment), then fall back to DefaultAzureCredential
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    
    # Parse the blob URL
    # Format: https://{account}.blob.core.windows.net/{container}/{blob_name}
    parts = image_url.replace("https://", "").split("/")
    account_url = f"https://{parts[0]}"
    container_name = parts[1]
    blob_name = "/".join(parts[2:])
    
    if connection_string:
        blob_service = BlobServiceClient.from_connection_string(connection_string)
    else:
        credential = DefaultAzureCredential()
        blob_service = BlobServiceClient(account_url=account_url, credential=credential)
    
    async with blob_service:
        blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
        download = await blob_client.download_blob()
        return await download.readall()


async def generate_image_description(client: AsyncAzureOpenAI, image_bytes: bytes, product_name: str, product_description: str) -> str:
    """
    Generate a detailed 2000-character description of a product image using GPT-4 Vision.
    
    Args:
        client: Azure OpenAI client
        image_bytes: Raw image bytes
        product_name: Name of the product
        product_description: Marketing description of the product
    
    Returns:
        Detailed image description (approximately 2000 characters)
    """
    # Convert image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = f"""Analyze this paint color swatch image for "{product_name}" and provide a detailed visual description that could be used to recreate this exact color and presentation in an AI image generator like DALL-E.

Product Context: {product_description}

Your description should be approximately 2000 characters and include:

1. **Exact Color Analysis**: Describe the precise hue, saturation, and brightness. Include RGB-style descriptions (e.g., "a soft blue-gray with hints of lavender"). Note any gradients, variations, or undertones visible in the swatch.

2. **Visual Texture & Finish**: Describe the paint's apparent finish (matte, satin, eggshell, glossy). Note any visible texture, brush strokes, or surface quality.

3. **Lighting & Shadows**: Describe how light interacts with the color - any highlights, shadows, or reflective qualities visible in the swatch.

4. **Color Relationships**: Describe what colors this would complement. Note warm vs cool tones, and how it might appear in different lighting conditions (daylight, incandescent, etc.).

5. **Mood & Atmosphere**: Describe the emotional quality and atmosphere this color evokes - is it calming, energizing, sophisticated, cozy?

6. **Room Application Suggestions**: Describe how this color might look on walls, in different room types, and what design styles it suits.

7. **Technical Color Details**: If possible, estimate the color in terms that could guide image generation - dominant wavelength, approximate hex range, comparison to well-known colors.

Write in a descriptive, visual style that would help an AI image generator accurately reproduce this paint color in marketing images. Be specific and evocative."""

    try:
        response = await client.chat.completions.create(
            model=app_settings.azure_openai.gpt_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=1000,
            temperature=0.7
        )
        
        description = response.choices[0].message.content
        
        # Ensure description is around 2000 characters (truncate if too long)
        if len(description) > 2200:
            # Find a good break point near 2000 chars
            description = description[:2000]
            last_period = description.rfind('.')
            if last_period > 1500:
                description = description[:last_period + 1]
        
        return description
        
    except Exception as e:
        print(f"    Warning: Failed to generate image description: {e}")
        return None


async def delete_existing_products():
    """Delete all existing products from CosmosDB."""
    print("Deleting existing products...")
    
    cosmos_service = await get_cosmos_service()
    deleted_count = await cosmos_service.delete_all_products()
    
    print(f"  ✓ Deleted {deleted_count} existing products.")
    return deleted_count


async def load_sample_data(generate_descriptions: bool = True):
    """Load sample products into CosmosDB with optional image description generation."""
    print("\nLoading Contoso Paints Catalog...")
    
    cosmos_service = await get_cosmos_service()
    openai_client = None
    
    if generate_descriptions:
        print("  Initializing GPT-4 Vision for image description generation...")
        try:
            openai_client = await get_openai_client()
            print("  ✓ GPT-4 Vision client initialized")
        except Exception as e:
            print(f"  ✗ Failed to initialize GPT-4 Vision: {e}")
            print("  Proceeding without image descriptions...")
            generate_descriptions = False
    
    loaded_count = 0
    for product_data in SAMPLE_PRODUCTS:
        try:
            product_name = product_data.get('product_name', 'unknown')
            
            # Generate image description if enabled
            if generate_descriptions and openai_client and product_data.get('image_url'):
                print(f"  Generating description for {product_name}...")
                try:
                    image_bytes = await get_image_from_blob(product_data['image_url'])
                    description = await generate_image_description(
                        client=openai_client,
                        image_bytes=image_bytes,
                        product_name=product_name,
                        product_description=product_data.get('description', '')
                    )
                    if description:
                        product_data['image_description'] = description
                        print(f"    ✓ Generated {len(description)} character description")
                except Exception as e:
                    print(f"    ✗ Failed to generate description: {e}")
            
            product = Product(**product_data)
            await cosmos_service.upsert_product(product)
            print(f"  ✓ Loaded: {product.product_name} ({product.sku})")
            loaded_count += 1
        except Exception as e:
            print(f"  ✗ Failed to load {product_data.get('product_name', 'unknown')}: {e}")
    
    print(f"\nLoaded {loaded_count} products from Contoso Paints Catalog.")


async def main(generate_descriptions: bool = True):
    """Main entry point."""
    try:
        # Delete existing products first
        await delete_existing_products()
        
        # Load new products with optional image description generation
        await load_sample_data(generate_descriptions=generate_descriptions)
    except Exception as e:
        print(f"Error loading sample data: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load sample product data into CosmosDB")
    parser.add_argument(
        "--skip-descriptions",
        action="store_true",
        help="Skip generating image descriptions using GPT-4 Vision"
    )
    parser.add_argument(
        "--generate-descriptions",
        action="store_true",
        default=True,
        help="Generate detailed image descriptions using GPT-4 Vision (default: True)"
    )
    
    args = parser.parse_args()
    
    generate_descriptions = not args.skip_descriptions
    
    print("=" * 60)
    print("Content Generation Solution Accelerator - Sample Data Loader")
    print("=" * 60)
    print(f"Image Description Generation: {'ENABLED' if generate_descriptions else 'DISABLED'}")
    print()
    
    asyncio.run(main(generate_descriptions=generate_descriptions))
