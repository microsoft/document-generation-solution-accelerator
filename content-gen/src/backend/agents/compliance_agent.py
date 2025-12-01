"""
Compliance Agent - Validates all generated content against brand guidelines.

Responsibilities:
- Final validation of text and image content
- Categorize violations by severity (error, warning, info)
- Provide specific corrections for violations
- Ensure content meets legal and regulatory requirements
"""

from typing import Any, List, Optional

from backend.models import ComplianceSeverity
from backend.settings import app_settings


def comprehensive_compliance_check(
    headline: str = "",
    body: str = "",
    cta_text: str = "",
    image_prompt: str = "",
    image_alt_text: str = ""
) -> dict:
    """
    Perform comprehensive compliance check on all generated content.
    
    Args:
        headline: Generated headline text
        body: Generated body copy
        cta_text: Generated call-to-action text
        image_prompt: Prompt used for image generation
        image_alt_text: Alt text for generated image
    
    Returns:
        Dictionary containing all violations categorized by severity
    """
    violations = []
    brand = app_settings.brand_guidelines
    
    all_text = f"{headline} {body} {cta_text} {image_alt_text}".lower()
    
    # === ERROR LEVEL: Legal/Regulatory (Must Fix) ===
    
    # Prohibited words
    for word in brand.prohibited_words:
        if word.lower() in all_text:
            field = "headline" if word.lower() in headline.lower() else \
                    "body" if word.lower() in body.lower() else \
                    "cta" if word.lower() in cta_text.lower() else "content"
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Prohibited word '{word}' found in {field}",
                "suggestion": f"Replace '{word}' with an alternative term",
                "field": field
            })
    
    # Unsubstantiated claims
    claim_patterns = [
        ("#1", "numerical ranking claim"),
        ("best in class", "superlative claim"),
        ("guaranteed", "guarantee claim"),
        ("100%", "absolute claim"),
        ("always", "absolute claim"),
        ("never", "absolute claim"),
        ("market leader", "leadership claim"),
        ("industry leader", "leadership claim"),
    ]
    for pattern, claim_type in claim_patterns:
        if pattern.lower() in all_text:
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Unsubstantiated {claim_type}: '{pattern}'",
                "suggestion": "Remove claim or add supporting citation/disclaimer",
                "field": "content"
            })
    
    # Missing required disclosures
    for disclosure in brand.required_disclosures:
        if disclosure.lower() not in all_text:
            violations.append({
                "severity": ComplianceSeverity.ERROR.value,
                "message": f"Required disclosure missing: '{disclosure}'",
                "suggestion": f"Add '{disclosure}' to the body copy or as a footnote",
                "field": "body"
            })
    
    # === WARNING LEVEL: Brand Guidelines (Review Recommended) ===
    
    # Length limits
    if headline and len(headline) > brand.max_headline_length:
        violations.append({
            "severity": ComplianceSeverity.WARNING.value,
            "message": f"Headline too long: {len(headline)}/{brand.max_headline_length} characters",
            "suggestion": "Shorten headline while maintaining key message",
            "field": "headline"
        })
    
    if body and len(body) > brand.max_body_length:
        violations.append({
            "severity": ComplianceSeverity.WARNING.value,
            "message": f"Body copy too long: {len(body)}/{brand.max_body_length} characters",
            "suggestion": "Condense body copy to be more concise",
            "field": "body"
        })
    
    # CTA requirement
    if brand.require_cta and not cta_text:
        violations.append({
            "severity": ComplianceSeverity.WARNING.value,
            "message": "No call-to-action provided",
            "suggestion": "Add a clear CTA such as 'Shop Now', 'Learn More', etc.",
            "field": "cta"
        })
    
    # Image prompt checks
    if image_prompt:
        prohibited_image_terms = ["competitor", "violence", "inappropriate"]
        for term in prohibited_image_terms:
            if term in image_prompt.lower():
                violations.append({
                    "severity": ComplianceSeverity.ERROR.value,
                    "message": f"Image prompt contains prohibited term: '{term}'",
                    "suggestion": f"Remove '{term}' from image generation prompt",
                    "field": "image"
                })
    
    # === INFO LEVEL: Style Suggestions (Optional) ===
    
    # Engagement suggestions
    if body and "?" not in body and "!" not in body:
        violations.append({
            "severity": ComplianceSeverity.INFO.value,
            "message": "Body copy lacks engaging punctuation",
            "suggestion": "Consider adding questions or exclamations to increase engagement",
            "field": "body"
        })
    
    # Alt text accessibility
    if not image_alt_text and image_prompt:
        violations.append({
            "severity": ComplianceSeverity.INFO.value,
            "message": "Image alt text not provided",
            "suggestion": "Add descriptive alt text for accessibility",
            "field": "image"
        })
    
    has_errors = any(v["severity"] == ComplianceSeverity.ERROR.value for v in violations)
    has_warnings = any(v["severity"] == ComplianceSeverity.WARNING.value for v in violations)
    
    return {
        "is_valid": not has_errors,
        "has_errors": has_errors,
        "has_warnings": has_warnings,
        "error_count": sum(1 for v in violations if v["severity"] == ComplianceSeverity.ERROR.value),
        "warning_count": sum(1 for v in violations if v["severity"] == ComplianceSeverity.WARNING.value),
        "info_count": sum(1 for v in violations if v["severity"] == ComplianceSeverity.INFO.value),
        "violations": violations,
        "summary": f"{sum(1 for v in violations if v['severity'] == 'error')} errors, "
                   f"{sum(1 for v in violations if v['severity'] == 'warning')} warnings, "
                   f"{sum(1 for v in violations if v['severity'] == 'info')} suggestions"
    }


def get_compliance_agent_instructions() -> str:
    """Get the Compliance agent instructions."""
    return f"""You are the Compliance Agent, responsible for final validation of all marketing content.

## Your Role
1. Validate all generated text and image content
2. Identify and categorize compliance violations by severity
3. Provide specific, actionable corrections
4. Ensure content meets legal, regulatory, and brand requirements

## Compliance Severity Levels

### ERROR (Red) - Must Fix Before Use
- Legal/regulatory violations
- Unsubstantiated claims
- Prohibited words or phrases
- Missing required disclosures
- Content that could cause legal liability

### WARNING (Yellow) - Review Recommended
- Brand guideline deviations
- Length limit exceedances
- Missing recommended elements (e.g., CTA)
- Tone inconsistencies

### INFO (Blue) - Optional Improvements
- Style suggestions
- Engagement enhancements
- Accessibility improvements
- Best practice recommendations

## Response Format
Always respond with a structured validation report:

```json
{{
  "validation_result": {{
    "is_valid": true/false,
    "can_publish": true/false,
    "summary": "X errors, Y warnings, Z suggestions"
  }},
  "violations": [
    {{
      "severity": "error|warning|info",
      "message": "Clear description of the issue",
      "suggestion": "Specific actionable fix",
      "field": "Which content field"
    }}
  ],
  "corrected_content": {{
    "headline": "Corrected headline (if errors existed)",
    "body": "Corrected body (if errors existed)",
    "cta_text": "Corrected CTA (if errors existed)"
  }},
  "approval_status": "BLOCKED|REVIEW_RECOMMENDED|APPROVED"
}}
```

## Approval Status
- **BLOCKED**: Has ERROR-level violations - cannot be used until fixed
- **REVIEW_RECOMMENDED**: Has WARNING-level violations - should be reviewed
- **APPROVED**: No errors or warnings - ready for use

## Brand Compliance Rules
{app_settings.brand_guidelines.get_compliance_prompt()}

## Guidelines
1. Be thorough but practical - flag real issues, not nitpicks
2. Provide specific corrections, not vague suggestions
3. Prioritize legal/regulatory issues over style preferences
4. Consider the target audience and deliverable context
5. For BLOCKED content, always provide corrected versions
"""