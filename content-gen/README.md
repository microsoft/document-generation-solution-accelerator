# Intelligent Content Generation Accelerator

A multimodal content generation solution for retail marketing campaigns using Microsoft Agent Framework with HandoffBuilder orchestration. The system interprets creative briefs and generates compliant marketing content (text and images) grounded in enterprise product data, brand guidelines, and product images.

## Overview

This accelerator provides an internal chatbot that can:

- **Interpret Creative Briefs**: Parse free-text creative briefs into structured fields (overview, objectives, target audience, key message, tone/style, deliverable, timelines, visual guidelines, CTA)
- **Generate Multimodal Content**: Create marketing copy and images using GPT-5 and DALL-E 3
- **Ensure Brand Compliance**: Validate all content against brand guidelines with severity-categorized warnings
- **Ground in Enterprise Data**: Leverage product information, product images, and brand guidelines stored in Azure services

## Architecture

### Specialized Agents (Microsoft Agent Framework)

The solution uses **HandoffBuilder** orchestration with 6 specialized agents:

| Agent | Role |
|-------|------|
| **TriageAgent** | Coordinator that routes user requests to appropriate specialists |
| **PlanningAgent** | Parses creative briefs, develops content strategy, returns for user confirmation |
| **ResearchAgent** | Retrieves products from CosmosDB, fetches brand guidelines, assembles grounding data |
| **TextContentAgent** | Generates marketing copy (headlines, body, CTAs) using GPT-5 |
| **ImageContentAgent** | Creates marketing images via DALL-E 3 with product context |
| **ComplianceAgent** | Validates content against brand guidelines, categorizes violations |

### Compliance Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **Error** | Legal/regulatory violations | Blocks acceptance until modified |
| **Warning** | Brand guideline deviations | Review recommended |
| **Info** | Style suggestions | Optional improvements |

### Data Storage

| Data | Storage | Purpose |
|------|---------|---------|
| Products | CosmosDB | Product catalog with auto-generated image descriptions |
| Chat History | CosmosDB | Conversation persistence |
| Product Images | Blob Storage | Seed images for DALL-E generation |
| Brand Guidelines | Solution Parameters | Injected into all agent instructions |

## Creative Brief Fields

The system extracts the following fields from free-text creative briefs:

1. **Overview** - Campaign summary
2. **Objectives** - Goals and KPIs
3. **Target Audience** - Demographics and psychographics
4. **Key Message** - Core messaging
5. **Tone and Style** - Voice and manner
6. **Deliverable** - Expected outputs
7. **Timelines** - Due dates and milestones
8. **Visual Guidelines** - Image requirements
9. **CTA** - Call to action

## Product Schema

```json
{
  "product_name": "string",
  "category": "string",
  "sub_category": "string",
  "marketing_description": "string",
  "detailed_spec_description": "string",
  "sku": "string",
  "model": "string",
  "image_description": "string (auto-generated via GPT-5 vision)",
  "image_url": "string"
}
```

## Getting Started

### Prerequisites

- Azure subscription with access to:
  - Azure AI Foundry (GPT-5 + DALL-E 3)
  - Azure CosmosDB
  - Azure Blob Storage
  - Azure App Service
- Azure Developer CLI (azd) >= 1.18.0
- Python 3.11+
- Node.js 18+

### Deployment

```bash
# Login to Azure
azd auth login

# Deploy infrastructure and application
azd up

# Upload product data (optional)
python ./scripts/product_ingestion.py
```

### Local Development

```bash
# Backend
cd src
pip install -r requirements.txt
python app.py

# Frontend
cd src/frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

See `src/backend/settings.py` for all configuration options. Key settings:

| Variable | Description |
|----------|-------------|
| `AZURE_AI_AGENT_ENDPOINT` | Azure AI Foundry project endpoint |
| `AZURE_OPENAI_MODEL` | GPT model deployment name (gpt-5) |
| `AZURE_DALLE_MODEL` | DALL-E model deployment name (dall-e-3) |
| `AZURE_COSMOSDB_ACCOUNT` | CosmosDB account name |
| `BRAND_*` | Brand guideline parameters |

### Brand Guidelines

Brand guidelines are configured via environment variables with the `BRAND_` prefix:

```env
BRAND_TONE=Professional yet approachable
BRAND_VOICE=Innovative, trustworthy, customer-focused
BRAND_PROHIBITED_WORDS=guarantee,best,only,exclusive
BRAND_REQUIRED_DISCLOSURES=Terms apply,See details
BRAND_PRIMARY_COLOR=#0078D4
BRAND_SECONDARY_COLOR=#107C10
```

## Documentation

- [DALL-E 3 Image Generation Limitations](docs/IMAGE_GENERATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Reference](docs/API.md)

## License

MIT License - See [LICENSE](LICENSE) for details.
