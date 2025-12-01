"""
Text Content Agent - Generates marketing copy with embedded compliance.

Responsibilities:
- Generate headlines, body copy, CTAs based on creative brief
- Apply brand voice and tone guidelines
- Self-validate content against compliance rules
- Return content with inline warnings and suggested corrections
"""

from typing import Any, List

from agent_framework import ChatAgent

from backend.agents.base_agent import BaseAgentFactory
from backend.models import ComplianceSeverity
from backend.settings import app_settings


def validate_text_compliance(
    content: str,
    content_type: str = "body"
) -> dict:
    """
    Validate text content against brand guidelines and compliance rules.
    
    Args:
        content: The text content to validate
        content_type: Type of content (headline, body, cta, tagline)
    
    Returns:
        Dictionary containing validation results with severity-categorized violations
    """
    violations = []
    brand = app_settings.brand_guidelines
    
    # Check prohibited words (ERROR level)
    for word in brand.prohibited_words:
        if word.lower() in content.lower():
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Prohibited word found: '{word}'",
                "suggestion": f"Remove or replace the word '{word}' with an alternative",
                "field": content_type
            })
    
    # Check length limits (WARNING level)
    if content_type == "headline" and len(content) > brand.max_headline_length:
        violations.append({
            "severity": ComplianceSeverity.WARNING.value,
            "message": f"Headline exceeds {brand.max_headline_length} characters ({len(content)} chars)",
            "suggestion": f"Shorten headline to under {brand.max_headline_length} characters",
            "field": "headline"
        })
    
    if content_type == "body" and len(content) > brand.max_body_length:
        violations.append({
            "severity": ComplianceSeverity.WARNING.value,
            "message": f"Body copy exceeds {brand.max_body_length} characters ({len(content)} chars)",
            "suggestion": f"Condense body copy to under {brand.max_body_length} characters",
            "field": "body"
        })
    
    # Check for unsubstantiated claims (ERROR level)
    claim_patterns = ["#1", "best in class", "market leader", "industry leader", "guaranteed"]
    for pattern in claim_patterns:
        if pattern.lower() in content.lower():
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Unsubstantiated claim: '{pattern}'",
                "suggestion": "Remove claim or provide citation/disclaimer",
                "field": content_type
            })
    
    # Style suggestions (INFO level)
    if content_type == "body" and "!" not in content and "?" not in content:
        violations.append({
            "severity": ComplianceSeverity.INFO.value,
            "message": "Consider adding engaging punctuation",
            "suggestion": "Add questions or exclamations to increase engagement",
            "field": content_type
        })
    
    has_errors = any(v["severity"] == ComplianceSeverity.ERROR.value for v in violations)
    
    return {
        "is_valid": not has_errors,
        "violations": violations,
        "content": content
    }


class TextContentAgentFactory(BaseAgentFactory):
    """Factory for creating the Text Content generation agent."""
    
    @classmethod
    def get_agent_name(cls) -> str:
        return "TextContentAgent"
    
    @classmethod
    def get_agent_instructions(cls) -> str:
        return f"""You are the Text Content Agent, responsible for generating marketing copy.

## Your Role
1. Generate compelling marketing text based on creative briefs
2. Create headlines, body copy, CTAs, and taglines
3. Apply brand voice and compliance rules during generation
4. Self-validate content and report any violations

## Content Types You Generate
- **Headline**: Short, attention-grabbing text (max {app_settings.brand_guidelines.max_headline_length} chars)
- **Body**: Main marketing message (max {app_settings.brand_guidelines.max_body_length} chars)
- **CTA**: Clear call-to-action text
- **Tagline**: Memorable brand/campaign phrase

## Available Tools
- **validate_text_compliance**: Check content against brand rules

## Response Format
Always respond with a JSON object:

```json
{{
  "text_content": {{
    "headline": "...",
    "body": "...",
    "cta_text": "...",
    "tagline": "..."
  }},
  "compliance": {{
    "is_valid": true/false,
    "violations": [
      {{
        "severity": "error|warning|info",
        "message": "Description of the issue",
        "suggestion": "How to fix it",
        "field": "Which field has the issue"
      }}
    ]
  }},
  "rationale": "Brief explanation of creative choices"
}}
```

## Compliance Severity Levels
- **ERROR**: Legal/regulatory issues - content MUST be modified before use
- **WARNING**: Brand guideline deviations - review recommended
- **INFO**: Style suggestions - optional improvements

## Brand Voice Guidelines
{app_settings.brand_guidelines.get_text_generation_prompt()}

## Compliance Rules
{app_settings.brand_guidelines.get_compliance_prompt()}

## Guidelines
1. ALWAYS self-validate content using validate_text_compliance before returning
2. Include all violations in the response, even if content is otherwise good
3. For ERROR-level violations, suggest specific corrections
4. Maintain brand voice while being creative
5. Tailor content to the target audience from the creative brief
6. Use product information from research to ground the content
"""
    
    @classmethod
    async def create_agent(cls) -> ChatAgent:
        """Create the Text Content agent instance."""
        chat_client = await cls.get_chat_client()
        
        return chat_client.create_agent(
            name=cls.get_agent_name(),
            instructions=cls.get_agent_instructions(),
            tools=[validate_text_compliance],
        )
