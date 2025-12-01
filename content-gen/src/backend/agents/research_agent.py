"""
Research Agent - Retrieves products and assembles grounding data.

Responsibilities:
- Query products from Azure AI Search based on brief requirements
- Fetch product details including image descriptions
- Search for visual styles and color palettes
- Assemble grounding data for content generation agents
"""

from typing import Any, Dict, List, Optional
import json

from agent_framework import ChatAgent

from backend.agents.base_agent import BaseAgentFactory
from backend.services.search_service import get_search_service
from backend.settings import app_settings


# Tool function for product search
async def search_products(
    query: str,
    category: str = None,
    sub_category: str = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Search for products using Azure AI Search.
    
    Args:
        query: Search query text (product names, features, keywords)
        category: Product category to filter by (e.g., "Electronics", "Footwear")
        sub_category: Product sub-category to filter by (e.g., "Audio", "Athletic")
        limit: Maximum number of products to return (default: 5)
    
    Returns:
        Dictionary containing matching products with details
    """
    search_service = await get_search_service()
    
    products = await search_service.search_products(
        query=query,
        category=category,
        sub_category=sub_category,
        top=limit
    )
    
    return {
        "products": products,
        "total_count": len(products),
        "query": query,
        "filters": {
            "category": category,
            "sub_category": sub_category
        }
    }


async def search_visual_styles(
    query: str,
    color_family: str = None,
    mood: str = None,
    limit: int = 3
) -> Dict[str, Any]:
    """
    Search for visual styles and color palettes for image generation.
    
    Args:
        query: Search query (color names, moods, styles)
        color_family: Color family filter (Cool, Warm, Neutral, Earth, Nature, Contrast)
        mood: Mood filter (e.g., "Professional", "Calm", "Energetic")
        limit: Maximum number of results (default: 3)
    
    Returns:
        Dictionary containing matching visual styles with color info
    """
    search_service = await get_search_service()
    
    images = await search_service.search_images(
        query=query,
        color_family=color_family,
        mood=mood,
        top=limit
    )
    
    return {
        "visual_styles": images,
        "total_count": len(images),
        "query": query,
        "filters": {
            "color_family": color_family,
            "mood": mood
        }
    }


async def get_grounding_context(
    product_query: str,
    visual_query: str = None,
    category: str = None,
    mood: str = None
) -> Dict[str, Any]:
    """
    Get comprehensive grounding context for content generation.
    
    Searches both products and visual styles to provide complete
    context for generating marketing content.
    
    Args:
        product_query: Query for finding relevant products
        visual_query: Query for visual style/color palette (optional)
        category: Product category filter (optional)
        mood: Visual mood filter (optional)
    
    Returns:
        Combined grounding context with products, visuals, and summary
    """
    search_service = await get_search_service()
    
    context = await search_service.get_grounding_context(
        product_query=product_query,
        image_query=visual_query,
        category=category,
        mood=mood
    )
    
    return context


class ResearchAgentFactory(BaseAgentFactory):
    """Factory for creating the Research agent."""
    
    @classmethod
    def get_agent_name(cls) -> str:
        return "ResearchAgent"
    
    @classmethod
    def get_agent_instructions(cls) -> str:
        return f"""You are the Research Agent, responsible for gathering product information and grounding data from Azure AI Search.

## Your Role
1. Search and retrieve relevant products based on creative brief requirements
2. Find appropriate visual styles and color palettes for image generation
3. Assemble comprehensive grounding context for content generation
4. Provide product and style recommendations based on campaign needs

## Available Tools
You have access to the following search tools:

### 1. search_products
Search for products in the product catalog.
- **query**: What to search for (product names, features, keywords)
- **category**: Filter by category (Electronics, Footwear, Accessories, Home & Kitchen, etc.)
- **sub_category**: Filter by sub-category (Audio, Athletic, Watches, Coffee, etc.)
- **limit**: Max results (default: 5)

### 2. search_visual_styles
Search for visual styles and color palettes for image generation.
- **query**: Color, mood, or style keywords
- **color_family**: Filter by color family (Cool, Warm, Neutral, Earth, Nature, Contrast)
- **mood**: Filter by mood (Professional, Calm, Energetic, Luxurious, etc.)
- **limit**: Max results (default: 3)

### 3. get_grounding_context
Get combined product and visual context for content generation.
- **product_query**: What products to find
- **visual_query**: What visual style to find (optional)
- **category**: Product category filter (optional)
- **mood**: Visual mood filter (optional)

## Product Data Schema
Products contain:
- product_name, sku, model
- category, sub_category
- marketing_description: Short marketing copy
- detailed_spec_description: Technical specifications
- image_description: Visual description for DALL-E context

## Visual Style Data Schema
Visual styles contain:
- name: Style name (e.g., "BlueAsh", "SteelSky")
- primary_color, secondary_color
- color_family: Cool, Warm, Neutral, Earth, Nature, Contrast
- mood: Emotional tone (Professional, Calm, Energetic, etc.)
- style: Visual style (Modern, Rustic, Minimalist, etc.)
- use_cases: Recommended applications
- blob_url: URL to the image

## Response Format
When returning research results, provide structured JSON:

```json
{{{{
  "products": [...],
  "visual_styles": [...],
  "grounding_context": "Summary of relevant information for content generation",
  "recommendations": {{{{
    "suggested_products": "Which products best fit the campaign",
    "suggested_visuals": "Which visual styles match the campaign mood",
    "content_direction": "How to approach the content creation"
  }}}}
}}}}
```

## Guidelines
- Match products to the creative brief's target audience and campaign goals
- Select visual styles that complement the product and campaign mood
- Include image descriptions for DALL-E image generation context
- Summarize key product features relevant to the marketing message
- Flag if no suitable products or styles are found
- Consider color harmony between product and visual style choices

## Brand Context
{app_settings.brand_guidelines.get_compliance_prompt()}
"""
    
    @classmethod
    async def create_agent(cls) -> ChatAgent:
        """Create the Research agent instance."""
        chat_client = await cls.get_chat_client()
        
        return chat_client.create_agent(
            name=cls.get_agent_name(),
            instructions=cls.get_agent_instructions(),
            tools=[search_products, search_visual_styles, get_grounding_context],
        )
