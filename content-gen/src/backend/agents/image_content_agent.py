"""
Image Content Agent - Generates marketing images via DALL-E 3.

Responsibilities:
- Create marketing images using DALL-E 3 based on creative brief
- Incorporate product descriptions as context (workaround for image seeding)
- Apply brand visual guidelines
- Validate generated images for compliance
"""

import base64
import logging
from typing import Any, Optional

from agent_framework import ChatAgent
from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential

from backend.agents.base_agent import BaseAgentFactory
from backend.models import ComplianceSeverity
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


def validate_image_prompt(prompt: str) -> dict:
    """
    Validate an image generation prompt against brand guidelines.
    
    Args:
        prompt: The image generation prompt to validate
    
    Returns:
        Dictionary containing validation results
    """
    violations = []
    brand = app_settings.brand_guidelines
    
    # Check for prohibited content (ERROR level)
    prohibited_terms = ["competitor", "violence", "inappropriate", "offensive"]
    for term in prohibited_terms:
        if term.lower() in prompt.lower():
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Prompt may generate prohibited content: '{term}'",
                "suggestion": f"Remove reference to '{term}' from the prompt",
                "field": "image_prompt"
            })
    
    # Check brand color mentions (INFO level)
    if brand.primary_color.lower() not in prompt.lower() and "brand color" not in prompt.lower():
        violations.append({
            "severity": ComplianceSeverity.INFO.value,
            "message": "Consider mentioning brand colors for consistency",
            "suggestion": f"Include reference to brand primary color {brand.primary_color}",
            "field": "image_prompt"
        })
    
    has_errors = any(v["severity"] == ComplianceSeverity.ERROR.value for v in violations)
    
    return {
        "is_valid": not has_errors,
        "violations": violations,
        "prompt": prompt
    }


class ImageContentAgentFactory(BaseAgentFactory):
    """Factory for creating the Image Content generation agent."""
    
    @classmethod
    def get_agent_name(cls) -> str:
        return "ImageContentAgent"
    
    @classmethod
    def get_agent_instructions(cls) -> str:
        return f"""You are the Image Content Agent, responsible for generating marketing images using DALL-E 3.

## Your Role
1. Create compelling marketing images based on creative briefs
2. Incorporate product context for accurate representation
3. Apply brand visual guidelines
4. Validate prompts before generation

## IMPORTANT: DALL-E 3 Limitation
DALL-E 3 only accepts text prompts - it cannot directly use product images as input.
To work around this, use the product's `image_description` field (auto-generated via GPT-5 Vision)
as detailed text context in your prompts.

## Available Tools
- **generate_dalle_image**: Generate an image using DALL-E 3
- **validate_image_prompt**: Check prompt for compliance issues

## Response Format
Always respond with a JSON object:

```json
{{
  "image_content": {{
    "image_base64": "base64 encoded image data",
    "prompt_used": "The full prompt sent to DALL-E",
    "alt_text": "Accessibility description of the image"
  }},
  "compliance": {{
    "is_valid": true/false,
    "violations": [
      {{
        "severity": "error|warning|info",
        "message": "Description of the issue",
        "suggestion": "How to fix it",
        "field": "image_prompt"
      }}
    ]
  }},
  "rationale": "Explanation of visual choices"
}}
```

## Brand Visual Guidelines
{app_settings.brand_guidelines.get_image_generation_prompt()}

## Guidelines for Effective Prompts
1. Be specific about composition, lighting, and style
2. Include product description context for accuracy
3. Mention brand colors when appropriate
4. Specify the intended use (social media, banner, etc.)
5. Request professional, high-quality output
6. Avoid mentioning competitors or prohibited content

## Prompt Structure
Build prompts with this structure:
1. Main subject and action
2. Product context (from image_description)
3. Setting/environment
4. Lighting and mood
5. Brand style elements
6. Technical requirements (composition, quality)

## Example Prompt Construction
For a wireless headphone social media ad:

"Professional marketing photo of sleek wireless headphones in matte black with rose gold accents.
The headphones are positioned on a minimalist white desk with subtle lifestyle elements.
Bright, natural lighting with soft shadows. Modern, clean aesthetic.
Incorporate brand blue (#0078D4) in background accents.
High-end product photography style, suitable for Instagram."
"""
    
    @classmethod
    async def create_agent(cls) -> ChatAgent:
        """Create the Image Content agent instance."""
        chat_client = await cls.get_chat_client()
        
        return chat_client.create_agent(
            name=cls.get_agent_name(),
            instructions=cls.get_agent_instructions(),
            tools=[generate_dalle_image, validate_image_prompt],
        )
