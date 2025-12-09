"""
Image Content Agent - Generates marketing images via DALL-E 3.

Provides the generate_dalle_image function used by the orchestrator
to create marketing images using DALL-E 3.
"""

import logging
import re
from typing import Any

from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential

from backend.settings import app_settings

logger = logging.getLogger(__name__)


def _truncate_for_dalle(product_description: str, max_chars: int = 1500) -> str:
    """
    Truncate product descriptions to fit DALL-E's 4000 character limit.
    Extracts the most visually relevant information (colors, hex codes, finishes).
    
    Args:
        product_description: The full product description(s)
        max_chars: Maximum characters to allow for product context
        
    Returns:
        Truncated description with essential visual details
    """
    if not product_description or len(product_description) <= max_chars:
        return product_description
    
    import re
    
    # Extract essential visual info: product names, hex codes, color descriptions
    lines = product_description.split('\n')
    essential_parts = []
    current_product = ""
    
    for line in lines:
        # Keep product name headers
        if line.startswith('### '):
            current_product = line
            essential_parts.append(line)
        # Keep hex code references
        elif 'hex' in line.lower() or '#' in line:
            if current_product and current_product not in essential_parts[-5:]:
                essential_parts.append(current_product)
            essential_parts.append(line.strip())
        # Keep first sentence of description (usually has the main color)
        elif line.strip().startswith('"') and 'appears as' in line.lower():
            # Extract first two sentences
            sentences = re.split(r'(?<=[.!?])\s+', line.strip())
            essential_parts.append(' '.join(sentences[:2]))
        # Keep finish descriptions
        elif 'finish' in line.lower() or 'matte' in line.lower() or 'eggshell' in line.lower():
            essential_parts.append(line.strip()[:200])
    
    result = '\n'.join(essential_parts)
    
    # If still too long, just truncate with ellipsis
    if len(result) > max_chars:
        result = result[:max_chars-50] + '\n\n[Additional details truncated for DALL-E]'
    
    return result


async def generate_dalle_image(
    prompt: str,
    product_description: str = "",
    scene_description: str = "",
    size: str = "1024x1024",
    quality: str = "hd"
) -> dict:
    """
    Generate a marketing image using DALL-E 3.
    
    Args:
        prompt: The main image generation prompt
        product_description: Auto-generated description of product image (for context)
        scene_description: Scene/setting description from creative brief
        size: Image size (1024x1024, 1024x1792, 1792x1024)
        quality: Image quality (standard, hd)
    
    Returns:
        Dictionary containing generated image data and metadata
    """
    brand = app_settings.brand_guidelines
    
    # DALL-E 3 has a 4000 character limit for prompts
    # Truncate product descriptions to essential visual info
    truncated_product_desc = _truncate_for_dalle(product_description, max_chars=1500)
    
    # Also truncate the main prompt if it's too long
    main_prompt = prompt[:1000] if len(prompt) > 1000 else prompt
    scene_desc = scene_description[:500] if scene_description and len(scene_description) > 500 else scene_description
    
    # Build the full prompt with product context and brand guidelines
    full_prompt = f"""
Create a professional marketing image.

{brand.get_image_generation_prompt()}

PRODUCT CONTEXT:
{truncated_product_desc if truncated_product_desc else 'No specific product - create a lifestyle/brand image'}

SCENE:
{scene_desc if scene_desc else main_prompt}

MAIN REQUIREMENT:
{main_prompt}

IMPORTANT:
- Create a polished, professional marketing image
- Suitable for retail advertising
- High visual impact
"""
    
    # Final safety check - DALL-E 3 has 4000 char limit
    if len(full_prompt) > 3900:
        logger.warning(f"Prompt too long ({len(full_prompt)} chars), truncating...")
        # Reduce product context further
        truncated_product_desc = _truncate_for_dalle(product_description, max_chars=800)
        full_prompt = f"""Create a professional marketing image.

PRODUCT: {truncated_product_desc[:600] if truncated_product_desc else 'Lifestyle/brand image'}

SCENE: {scene_desc[:300] if scene_desc else main_prompt[:300]}

REQUIREMENT: {main_prompt[:500]}

Style: Modern, clean, minimalist. Brand colors: {brand.primary_color}, {brand.secondary_color}. High visual impact for retail advertising.
"""

    try:
        # Get credential
        client_id = app_settings.base_settings.azure_client_id
        if client_id:
            credential = ManagedIdentityCredential(client_id=client_id)
        else:
            credential = DefaultAzureCredential()
        
        # Get token for Azure OpenAI
        token = await credential.get_token("https://cognitiveservices.azure.com/.default")
        
        # Use the dedicated DALL-E endpoint if configured, otherwise fall back to main endpoint
        dalle_endpoint = app_settings.azure_openai.dalle_endpoint or app_settings.azure_openai.endpoint
        logger.info(f"Using DALL-E endpoint: {dalle_endpoint}")
        
        client = AsyncAzureOpenAI(
            azure_endpoint=dalle_endpoint,
            azure_ad_token=token.token,
            api_version=app_settings.azure_openai.preview_api_version,
        )
        
        response = await client.images.generate(
            model=app_settings.azure_openai.dalle_model,
            prompt=full_prompt,
            size=size,
            quality=quality,
            n=1,
            response_format="b64_json"
        )
        
        image_data = response.data[0]
        
        return {
            "success": True,
            "image_base64": image_data.b64_json,
            "prompt_used": full_prompt,
            "revised_prompt": getattr(image_data, 'revised_prompt', None),
        }
        
    except Exception as e:
        logger.exception(f"Error generating DALL-E image: {e}")
        return {
            "success": False,
            "error": str(e),
            "prompt_used": full_prompt
        }
