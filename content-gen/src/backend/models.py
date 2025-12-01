"""
Data models for the Intelligent Content Generation Accelerator.

This module defines Pydantic models for:
- Creative briefs (parsed from free-text input)
- Products (stored in CosmosDB)
- Compliance validation results
- Generated content responses
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ComplianceSeverity(str, Enum):
    """Severity levels for compliance violations."""
    ERROR = "error"      # Legal/regulatory - blocks until modified
    WARNING = "warning"  # Brand guideline deviation - review recommended
    INFO = "info"        # Style suggestion - optional


class ComplianceViolation(BaseModel):
    """A single compliance violation with severity and suggested fix."""
    severity: ComplianceSeverity
    message: str
    suggestion: str
    field: Optional[str] = None  # Which field the violation relates to


class ComplianceResult(BaseModel):
    """Result of compliance validation on generated content."""
    is_valid: bool = Field(description="True if no error-level violations")
    violations: List[ComplianceViolation] = Field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level violations."""
        return any(v.severity == ComplianceSeverity.ERROR for v in self.violations)
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warning-level violations."""
        return any(v.severity == ComplianceSeverity.WARNING for v in self.violations)


class CreativeBrief(BaseModel):
    """
    Structured creative brief parsed from free-text input.
    
    The PlanningAgent extracts these fields from user's natural language
    creative brief description.
    """
    overview: str = Field(description="Campaign summary and context")
    objectives: str = Field(description="Goals and KPIs for the campaign")
    target_audience: str = Field(description="Demographics and psychographics")
    key_message: str = Field(description="Core messaging and value proposition")
    tone_and_style: str = Field(description="Voice, manner, and communication style")
    deliverable: str = Field(description="Expected outputs (e.g., social posts, banners)")
    timelines: str = Field(description="Due dates and milestones")
    visual_guidelines: str = Field(description="Image requirements and visual direction")
    cta: str = Field(description="Call to action text and placement")
    
    # Metadata
    raw_input: Optional[str] = Field(default=None, description="Original free-text input")
    confidence_score: Optional[float] = Field(default=None, description="Extraction confidence 0-1")


class Product(BaseModel):
    """
    Product information stored in CosmosDB.
    
    Image descriptions are auto-generated via GPT-5 Vision during
    product ingestion to enable DALL-E 3 text-based image generation.
    """
    id: Optional[str] = None
    product_name: str = Field(description="Display name of the product")
    category: str = Field(description="Primary product category")
    sub_category: Optional[str] = Field(default=None, description="Secondary category")
    marketing_description: str = Field(description="Short marketing copy for the product")
    detailed_spec_description: str = Field(description="Detailed specifications")
    sku: str = Field(description="Stock keeping unit identifier")
    model: Optional[str] = Field(default=None, description="Model number or name")
    image_description: Optional[str] = Field(
        default=None, 
        description="Auto-generated text description of product image via GPT-5 Vision"
    )
    image_url: Optional[str] = Field(default=None, description="URL to product image in Blob Storage")
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GeneratedTextContent(BaseModel):
    """Generated marketing text content with compliance status."""
    headline: Optional[str] = None
    body: Optional[str] = None
    cta_text: Optional[str] = None
    tagline: Optional[str] = None
    compliance: ComplianceResult = Field(default_factory=ComplianceResult)


class GeneratedImageContent(BaseModel):
    """Generated marketing image content with compliance status."""
    image_base64: str = Field(description="Base64-encoded image data")
    image_url: Optional[str] = Field(default=None, description="URL if saved to Blob Storage")
    prompt_used: str = Field(description="DALL-E prompt that generated the image")
    alt_text: str = Field(description="Accessibility alt text for the image")
    compliance: ComplianceResult = Field(default_factory=ComplianceResult)


class ContentGenerationResponse(BaseModel):
    """Complete response from content generation workflow."""
    text_content: Optional[GeneratedTextContent] = None
    image_content: Optional[GeneratedImageContent] = None
    creative_brief: CreativeBrief
    products_used: List[str] = Field(default_factory=list, description="Product IDs used")
    generation_id: str = Field(description="Unique ID for this generation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def requires_modification(self) -> bool:
        """Check if content has error-level violations requiring modification."""
        text_has_errors = self.text_content and self.text_content.compliance.has_errors
        image_has_errors = self.image_content and self.image_content.compliance.has_errors
        return text_has_errors or image_has_errors


class ConversationMessage(BaseModel):
    """A message in the chat conversation."""
    id: str
    role: str = Field(description="user, assistant, or system")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    feedback: Optional[str] = None
    
    # For multimodal responses
    image_base64: Optional[str] = None
    compliance_warnings: Optional[List[ComplianceViolation]] = None


class Conversation(BaseModel):
    """A conversation session stored in CosmosDB."""
    id: str
    user_id: str
    title: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    creative_brief: Optional[CreativeBrief] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BriefConfirmationRequest(BaseModel):
    """Request to confirm or edit a parsed creative brief."""
    conversation_id: str
    creative_brief: CreativeBrief
    confirmed: bool = False
    edits: Optional[dict] = None  # Field-level edits to apply


class ContentIterationRequest(BaseModel):
    """Request to iterate on generated content with additional direction."""
    conversation_id: str
    generation_id: str
    feedback: str = Field(description="User's feedback or additional direction")
    regenerate_text: bool = False
    regenerate_image: bool = False
