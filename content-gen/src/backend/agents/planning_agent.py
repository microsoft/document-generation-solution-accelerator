"""
Planning Agent - Parses creative briefs and develops content strategy.

Responsibilities:
- Parse free-text creative briefs into structured 9-field format
- Develop content strategy based on brief requirements
- Return parsed brief for user confirmation before content generation
"""

import json
from typing import Any

from agent_framework import ChatAgent

from backend.agents.base_agent import BaseAgentFactory
from backend.settings import app_settings


class PlanningAgentFactory(BaseAgentFactory):
    """Factory for creating the Planning agent."""
    
    @classmethod
    def get_agent_name(cls) -> str:
        return "PlanningAgent"
    
    @classmethod
    def get_agent_instructions(cls) -> str:
        return f"""You are the Planning Agent, responsible for parsing creative briefs and developing content strategy.

## Your Role
1. Accept free-text creative brief descriptions from users
2. Extract and structure the information into the 9 required fields
3. Develop a content strategy based on the brief
4. Return the parsed brief for user confirmation

## Creative Brief Fields to Extract
Parse the user's input to identify these 9 fields:

1. **Overview**: Campaign summary and context
2. **Objectives**: Goals, KPIs, and success metrics
3. **Target Audience**: Demographics, psychographics, and customer segments
4. **Key Message**: Core messaging and value proposition
5. **Tone and Style**: Voice, manner, and communication style
6. **Deliverable**: Expected outputs (e.g., social posts, banners, email)
7. **Timelines**: Due dates, milestones, and scheduling
8. **Visual Guidelines**: Image requirements and visual direction
9. **CTA**: Call to action text and placement

## Response Format
Always respond with a JSON object containing the parsed brief:

```json
{{
  "creative_brief": {{
    "overview": "...",
    "objectives": "...",
    "target_audience": "...",
    "key_message": "...",
    "tone_and_style": "...",
    "deliverable": "...",
    "timelines": "...",
    "visual_guidelines": "...",
    "cta": "..."
  }},
  "confidence_score": 0.85,
  "missing_fields": ["list of fields that need clarification"],
  "suggested_products": ["relevant product categories based on brief"],
  "content_strategy": "Brief description of recommended approach"
}}
```

## Guidelines
- If a field is not explicitly mentioned, infer from context or mark as needing clarification
- Provide a confidence score (0-1) for the overall extraction quality
- List any fields that are ambiguous or missing
- Suggest relevant product categories that might be needed
- Keep the user informed about what's been understood and what needs clarification

## Brand Context
{app_settings.brand_guidelines.get_text_generation_prompt()}

## Example Interaction
User: "We need a summer campaign for our new wireless headphones targeting young professionals. Fun and energetic vibe, launching next month on social media."

Your response should extract:
- Overview: Summer campaign for wireless headphones launch
- Target Audience: Young professionals
- Tone and Style: Fun and energetic
- Deliverable: Social media content
- Timelines: Next month
- And infer/request missing details for other fields
"""
    
    @classmethod
    async def create_agent(cls) -> ChatAgent:
        """Create the Planning agent instance."""
        chat_client = await cls.get_chat_client()
        
        return chat_client.create_agent(
            name=cls.get_agent_name(),
            instructions=cls.get_agent_instructions(),
        )
