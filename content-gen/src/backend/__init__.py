"""
Backend package for Content Generation Solution Accelerator.

This package contains:
- models: Data models (CreativeBrief, Product, ComplianceViolation, etc.)
- settings: Application configuration and brand guidelines
- agents: Specialized AI agents for content generation
- services: CosmosDB and Blob Storage services
- orchestrator: HandoffBuilder-based multi-agent orchestration
"""

from backend.models import (
    CreativeBrief,
    Product,
    ComplianceViolation,
    ComplianceSeverity,
    ContentGenerationResponse,
    ComplianceResult,
)
from backend.settings import app_settings

__all__ = [
    "CreativeBrief",
    "Product",
    "ComplianceViolation",
    "ComplianceSeverity",
    "ContentGenerationResponse",
    "ComplianceResult",
    "app_settings",
]
