# Content Generation Solution Accelerator - Transition Document

**Date:** January 16, 2026  
**Prepared for:** Incoming Engineer  
**Repository:** https://github.com/hunterjam/content-generation-solution-accelerator  
**Upstream:** https://github.com/microsoft/document-generation-solution-accelerator

---

## 1. Project Overview

This is a **multimodal content generation solution** for retail marketing campaigns. It uses Microsoft Agent Framework with HandoffBuilder orchestration to interpret creative briefs and generate compliant marketing content (text + images) grounded in enterprise product data and brand guidelines.

### Key Capabilities
- Parse free-text creative briefs into structured fields
- Generate marketing copy using GPT models
- Generate marketing images using DALL-E 3
- Validate content against brand guidelines with severity-categorized compliance checks
- Ground content in product catalog data from Cosmos DB

---

## 2. System Architecture & How It Works

### High-Level Flow

```
User → Frontend (React) → Backend API (Python/Quart) → Agent Orchestrator → Azure OpenAI
                                                              ↓
                                                      Multi-Agent System
                                                              ↓
                                              ┌───────────────┼───────────────┐
                                              ↓               ↓               ↓
                                        TriageAgent → PlanningAgent → ResearchAgent
                                              ↓               ↓               ↓
                                    TextContentAgent  ImageContentAgent  ComplianceAgent
                                              ↓               ↓               ↓
                                              └───────────────┼───────────────┘
                                                              ↓
                                                    Generated Content
                                                    (Text + Image + Compliance)
```

### The Agent System

The solution uses **Microsoft Agent Framework** with **HandoffBuilder orchestration**. This means agents can dynamically hand off control to each other based on context. Here's how each agent works:

| Agent | Responsibility | Inputs | Outputs |
|-------|---------------|--------|---------|
| **TriageAgent** | Coordinator - routes requests to the right specialist | User message | Handoff decision |
| **PlanningAgent** | Parses creative briefs into structured fields, asks clarifying questions if info is missing | Free-text brief | Structured `CreativeBrief` JSON |
| **ResearchAgent** | Retrieves product data from Cosmos DB, fetches brand guidelines | Product queries | Product details, brand info |
| **TextContentAgent** | Generates marketing copy (headlines, body, CTAs, hashtags) | Brief + Products | Marketing copy JSON |
| **ImageContentAgent** | Creates DALL-E prompts and generates images | Brief + Products | Image URL + prompt |
| **ComplianceAgent** | Validates content against brand guidelines | Generated content | Violations list with severity |

### Content Generation Workflow

When a user submits a creative brief, this is what happens:

1. **Brief Parsing** (PlanningAgent)
   - User submits free-text brief like "Create a spring campaign for our new green paint colors"
   - PlanningAgent extracts structured fields: objectives, target audience, key message, tone, deliverables
   - If critical fields are missing, agent asks clarifying questions
   - User confirms the parsed brief

2. **Product Selection** (ResearchAgent)
   - System queries Cosmos DB for matching products
   - Products are presented to user for confirmation
   - User can add/remove products from selection

3. **Content Generation** (TextContentAgent + ImageContentAgent)
   - **Text**: GPT generates headline, body copy, CTA, hashtags based on brief + products
   - **Image**: DALL-E generates marketing image with product context
   - If product has an image (`image_url`), it's overlaid on the generated background

4. **Compliance Check** (ComplianceAgent)
   - Validates content against brand guidelines
   - Returns violations categorized by severity:
     - **Error**: Must fix before use (blocks acceptance)
     - **Warning**: Review recommended
     - **Info**: Optional improvements

5. **Response to User**
   - Frontend displays generated content with compliance status
   - User can regenerate, modify, or accept

### Key Data Structures

**CreativeBrief** (what the PlanningAgent extracts):
```typescript
{
  overview: string;        // Campaign summary
  objectives: string;      // Goals and KPIs
  target_audience: string; // Who it's for
  key_message: string;     // Core value proposition
  tone_and_style: string;  // Voice (professional, playful, etc.)
  deliverable: string;     // Output type (social post, email, etc.)
  timelines: string;       // Deadlines
  visual_guidelines: string; // Image style requirements
  cta: string;             // Call to action
}
```

**Product** (from Cosmos DB):
```typescript
{
  product_name: string;
  description: string;
  tags: string;
  price: number;
  sku: string;
  image_url?: string;      // Product image for overlay
  hex_value?: string;      // Color hex code for paint products
}
```

**GeneratedContent** (what the system produces):
```typescript
{
  text_content: {
    headline: string;
    body: string;
    cta_text: string;
    tagline: string;
  };
  image_content: {
    image_url: string;     // Generated or composite image
    alt_text: string;
    prompt_used: string;   // The DALL-E prompt
  };
  violations: ComplianceViolation[];
  requires_modification: boolean;  // True if any "error" violations
}
```

### Image Generation Details

The image generation has special logic for **product overlay**:

1. If the product has an `image_url` (e.g., a paint can image):
   - DALL-E generates a **background scene** (e.g., living room with the paint color)
   - The product image is **composited** onto the background
   - This ensures the actual product packaging appears in the marketing image

2. If no product image:
   - DALL-E generates a complete scene
   - No overlay is applied

3. **Text-free images**: The system instructs DALL-E to generate images without text overlays, as text rendering in AI images is often poor quality.

### Frontend-Backend Communication

The frontend uses **Server-Sent Events (SSE)** for streaming responses:

1. Frontend calls `/api/generate/start` with brief + products
2. Backend returns a `task_id` immediately
3. Frontend polls `/api/generate/status/{task_id}` every second
4. Backend returns progress updates (heartbeats with stage info)
5. When complete, backend returns the full `GeneratedContent`

This polling approach handles the 30-60 second generation time without timeouts.

### Content Safety

The system has multiple layers of content safety:

1. **Input filtering** (`orchestrator.py`): Regex patterns block harmful requests before they reach agents
2. **Agent instructions**: Each agent has explicit refusal instructions for inappropriate content
3. **Azure OpenAI content filters**: Built-in filters on the AI models
4. **Compliance validation**: Final check against brand guidelines

---

## 3. Repository Structure

```
content-generation-solution-accelerator/
├── content-gen/                    # Main application (THIS IS THE ACTIVE CODE)
│   ├── src/
│   │   ├── app/                    # Frontend application
│   │   │   ├── frontend/           # React + Vite + TypeScript + Fluent UI
│   │   │   │   └── src/
│   │   │   │       ├── components/ # React components
│   │   │   │       ├── api/        # API client functions
│   │   │   │       └── types/      # TypeScript interfaces
│   │   │   └── WebApp.Dockerfile   # Frontend container build
│   │   └── backend/                # Python backend
│   │       ├── agents/             # AI agent implementations
│   │       ├── api/                # API route handlers
│   │       ├── services/           # Business logic services
│   │       ├── orchestrator.py     # Agent orchestration logic
│   │       ├── settings.py         # Configuration/environment
│   │       └── ApiApp.Dockerfile   # Backend container build
│   ├── scripts/                    # Deployment and data scripts
│   │   └── post_deploy.py          # Product data seeding
│   ├── infra/                      # Bicep infrastructure as code
│   └── docs/                       # Documentation
├── archive-doc-gen/                # Legacy document generation (separate app)
└── docs/                           # Root-level documentation
```

---

## 4. Key Files Reference

### Backend
| File | Purpose |
|------|---------|
| `src/backend/orchestrator.py` | Main agent orchestration, content generation workflow |
| `src/backend/agents/image_content_agent.py` | DALL-E image generation logic |
| `src/backend/settings.py` | All environment variables and configuration |
| `src/backend/api/` | REST API endpoints |
| `src/backend/services/` | Cosmos DB, storage, AI service integrations |

### Frontend
| File | Purpose |
|------|---------|
| `src/app/frontend/src/App.tsx` | Main React application |
| `src/app/frontend/src/components/ChatPanel.tsx` | Main chat interface |
| `src/app/frontend/src/components/InlineContentPreview.tsx` | Content display with compliance status |
| `src/app/frontend/src/api/index.ts` | API client functions |
| `src/app/frontend/src/types/index.ts` | TypeScript type definitions |

### Deployment
| File | Purpose |
|------|---------|
| `scripts/post_deploy.py` | Seeds sample product data to Cosmos DB |
| `infra/main.bicep` | Azure infrastructure definition |
| `azure.yaml` | Azure Developer CLI configuration |

---

## 5. Recent Changes (Last Session)

### Commits Merged to Main

1. **Fix image generation overlay handling** - Improved how product images are overlaid on generated backgrounds
2. **Fix product/campaign logic** - Corrected color descriptions for paint products (Quiet Moss, Cloud Drift, Pine Shadow)
3. **Add multi-product handling instructions** - Enhanced orchestrator to handle campaigns with multiple products
4. **Add user guidance callouts** - Added clear "Action needed" / "Optional review" messages in UI for compliance status
5. **Remove unused components** - Cleaned up dead code:
   - `ContentPreview.tsx` (replaced by `InlineContentPreview.tsx`)
   - `TaskHeader.tsx`
   - Unused API functions (`getProducts`, `uploadProductImage`, `getBrandGuidelines`, `getConversations`, `getConversation`)
   - Unused types (`ComplianceSeverity`, `ContentResponse`)

### Important Discovery
The frontend uses **`InlineContentPreview.tsx`** for displaying generated content, NOT `ContentPreview.tsx`. The latter was dead code and has been removed.

---

## 6. Development Workflow

### Local Development

```bash
# Backend
cd content-gen/src/backend
pip install -r requirements.txt
python app.py

# Frontend
cd content-gen/src/app/frontend
npm install
npm run dev
```

### Building & Deploying Containers

```bash
# Build and push frontend (using ACR build)
az acr build --registry <your-acr-name> \
  --image content-gen-webapp:latest \
  --file content-gen/src/app/WebApp.Dockerfile \
  content-gen/src/app

# Build and push backend
az acr build --registry <your-acr-name> \
  --image content-gen-api:latest \
  --file content-gen/src/backend/ApiApp.Dockerfile \
  content-gen/src/backend

# Restart services to pull new images
az webapp restart --name <webapp-name> --resource-group <resource-group>
az container restart --name <container-name> --resource-group <resource-group>
```

---

## 7. Git Workflow

### Branches
- `main` - Production branch
- `fix-image-generation-overlay` - Recent image generation fixes (merged)
- `cleanup-unused-frontend-code` - Code cleanup (merged)

### Remotes
- `origin` - Fork: `hunterjam/content-generation-solution-accelerator`
- `upstream` - Microsoft repo: `microsoft/document-generation-solution-accelerator`

### Syncing with Upstream
```bash
git fetch upstream
git merge upstream/main
```

---

## 8. Environment Variables

Key settings in `src/backend/settings.py`:

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint for GPT |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | GPT model deployment name |
| `AZURE_OPENAI_DALLE_ENDPOINT` | DALL-E endpoint (if separate) |
| `AZURE_OPENAI_DALLE_DEPLOYMENT` | DALL-E deployment name |
| `COSMOS_ENDPOINT` | Cosmos DB endpoint |
| `COSMOS_DATABASE` | Database name |
| `AZURE_STORAGE_ACCOUNT_NAME` | Blob storage account |
| `ENABLE_IMAGE_GENERATION` | Toggle image generation feature |

---

## 9. Useful Commands

```bash
# View container logs
az webapp log tail --name <webapp-name> --resource-group <resource-group>

# Check container configuration
az webapp config container show --name <webapp-name> --resource-group <resource-group>

# List ACR images
az acr repository list --name <acr-name>

# Check image tags
az acr repository show-tags --name <acr-name> --repository content-gen-webapp
```

---

## 10. Contact & Resources

- **Project README:** `content-gen/README.md`
- **Deployment Docs:** `content-gen/docs/`
- **Upstream Issues:** https://github.com/microsoft/document-generation-solution-accelerator/issues

---

## 11. Quick Start for New Engineer

1. **Clone and setup:**
   ```bash
   git clone https://github.com/hunterjam/content-generation-solution-accelerator.git
   cd content-generation-solution-accelerator
   ```

2. **Open in VS Code with Dev Container** (recommended)

3. **Login to Azure:**
   ```bash
   az login
   az account set --subscription <subscription-id>
   az acr login --name <your-acr-name>
   ```

4. **Run locally:**
   ```bash
   # Terminal 1 - Backend
   cd content-gen/src/backend
   pip install -r requirements.txt
   # Set environment variables (see settings.py)
   python app.py

   # Terminal 2 - Frontend
   cd content-gen/src/app/frontend
   npm install
   npm run dev
   ```

5. **Make changes and deploy:**
   ```bash
   # After code changes
   git checkout -b feature/your-feature
   # Make changes...
   git commit -am "Your change"
   
   # Build and deploy (replace placeholders with your Azure resources)
   az acr build --registry <your-acr-name> --image content-gen-webapp:latest \
     --file content-gen/src/app/WebApp.Dockerfile content-gen/src/app
   az webapp restart --name <webapp-name> --resource-group <resource-group>
   ```

---

*Document generated: January 16, 2026*
