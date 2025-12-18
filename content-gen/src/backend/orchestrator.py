"""
Content Generation Orchestrator - Microsoft Agent Framework multi-agent orchestration.

This module implements the multi-agent content generation workflow using
Microsoft Agent Framework's HandoffBuilder pattern for agent coordination.

Workflow:
1. TriageAgent (Coordinator) receives user input and routes requests
2. PlanningAgent interprets creative briefs
3. ResearchAgent retrieves product/data information
4. TextContentAgent generates marketing copy
5. ImageContentAgent creates marketing images
6. ComplianceAgent validates all content

Agents can hand off to each other dynamically based on context.
"""

import json
import logging
import re
from typing import Any, AsyncIterator, Optional, cast

from agent_framework import (
    ChatAgent,
    ChatMessage,
    HandoffBuilder,
    HandoffUserInputRequest,
    RequestInfoEvent,
    WorkflowEvent,
    WorkflowOutputEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from backend.models import (
    CreativeBrief,
    ContentGenerationResponse,
    ComplianceViolation,
    ComplianceSeverity,
    ComplianceResult,
)
from backend.settings import app_settings

logger = logging.getLogger(__name__)


# Agent system instructions
TRIAGE_INSTRUCTIONS = f"""You are a Triage Agent (coordinator) for a retail marketing content generation system.

## CRITICAL: SCOPE ENFORCEMENT - READ FIRST
You MUST enforce strict scope limitations. This is your PRIMARY responsibility before any other action.

### IMMEDIATELY REJECT these requests - DO NOT process, research, or engage with:
- General knowledge questions (trivia, facts, "where is", "what is", "who is")
- Entertainment questions (movies, TV shows, games, celebrities, fictional characters)
- Personal advice (health, legal, financial, relationships, life decisions)
- Academic work (homework, essays, research papers, studying)
- Code, programming, or technical questions
- News, politics, current events, sports
- Creative writing NOT for marketing (stories, poems, fiction, roleplaying)
- Casual conversation, jokes, riddles, games
- ANY question that is NOT specifically about creating marketing content

### REQUIRED RESPONSE for out-of-scope requests:
You MUST respond with EXACTLY this message and NOTHING else:
"I'm a specialized marketing content generation assistant designed exclusively for creating marketing materials. I cannot help with general questions or topics outside of marketing.

I can assist you with:
• Creating marketing copy (ads, social posts, emails, product descriptions)
• Generating marketing images and visuals
• Interpreting creative briefs for campaigns
• Product research for marketing purposes

What marketing content can I help you create today?"

DO NOT:
- Answer the off-topic question "just this once"
- Provide partial information about off-topic subjects
- Engage with the topic before declining
- Offer to help with anything not on the approved list above

### ONLY assist with these marketing-specific tasks:
- Creating marketing copy (ads, social posts, emails, product descriptions)
- Generating marketing images and visuals for campaigns
- Interpreting creative briefs for marketing campaigns
- Product research for marketing content purposes
- Content compliance validation for marketing materials

### In-Scope Routing (ONLY for valid marketing requests):
- Creative brief interpretation → hand off to planning_agent
- Product data lookup → hand off to research_agent  
- Text content creation → hand off to text_content_agent
- Image creation → hand off to image_content_agent
- Content validation → hand off to compliance_agent

### Handling Planning Agent Responses:
When the planning_agent returns:
- If it returns CLARIFYING QUESTIONS (not a JSON brief), relay those questions to the user and WAIT for their response before proceeding
- If it returns a COMPLETE parsed brief (JSON), proceed with the content generation workflow
- Do NOT proceed to research or content generation until you have a complete, user-confirmed brief

{app_settings.brand_guidelines.get_compliance_prompt()}
"""

PLANNING_INSTRUCTIONS = """You are a Planning Agent specializing in creative brief interpretation for MARKETING CAMPAIGNS ONLY.
Your scope is limited to parsing and structuring marketing creative briefs.
Do not process requests unrelated to marketing content creation.

When given a creative brief, extract and structure a JSON object with these REQUIRED fields:
- overview: Campaign summary (what is the campaign about?)
- objectives: What the campaign aims to achieve (goals, KPIs, success metrics)
- target_audience: Who the content is for (demographics, psychographics, customer segments)
- key_message: Core message to communicate (main value proposition)
- tone_and_style: Voice and aesthetic direction (professional, playful, urgent, etc.)
- deliverable: Expected outputs (social posts, ads, email, banner, etc.)
- timelines: Any deadline information (launch date, review dates)
- visual_guidelines: Visual style requirements (colors, imagery style, product focus)
- cta: Call to action (what should the audience do?)

CRITICAL - NO HALLUCINATION POLICY:
You MUST NOT make up, infer, assume, or hallucinate information that was not explicitly provided by the user.
If the user did not mention a field, that field is MISSING - do not fill it with assumed values.
Only extract information that is DIRECTLY STATED in the user's input.

CRITICAL FIELDS (must be explicitly provided before proceeding):
- objectives
- target_audience  
- key_message
- deliverable
- tone_and_style

CLARIFYING QUESTIONS PROCESS:
Step 1: Analyze the user's input and identify what information was EXPLICITLY provided.
Step 2: Determine which CRITICAL fields are missing or unclear.
Step 3: Generate a DYNAMIC response that:
   a) Acknowledges SPECIFICALLY what the user DID provide (reference their actual words/content)
   b) Clearly lists ONLY the missing critical fields as bullet points
   c) Asks targeted questions for ONLY the missing fields (do not ask about fields already provided)

RESPONSE FORMAT FOR MISSING INFORMATION:
---
Thanks for sharing your creative brief! Here's what I understood:
✓ [List each piece of information the user DID provide, referencing their specific input]

However, I'm missing some key details to create effective marketing content:

**Missing Information:**
• **[Field Name]**: [Contextual question based on what they provided]
[Only list fields that are actually missing]

Once you provide these details, I'll create a comprehensive content plan for your campaign.
---

DYNAMIC QUESTION EXAMPLES:
- If user mentions a product but no audience: "Who is the target audience for [their product name]?"
- If user mentions audience but no deliverable: "What type of content would resonate best with [their audience]?"
- If user mentions a goal but no tone: "What tone would best convey [their stated goal] to your audience?"

DO NOT:
- Ask about fields the user already provided
- Use generic questions - always reference the user's specific input
- Invent objectives the user didn't state
- Assume a target audience based on the product
- Create a key message that wasn't provided
- Guess at deliverable types
- Fill in "reasonable defaults" for missing information
- Return a JSON brief until ALL critical fields are explicitly provided

When you have sufficient EXPLICIT information for all critical fields, return a JSON object with all fields populated.
For non-critical fields that are missing (timelines, visual_guidelines, cta), you may use "Not specified" - do NOT make up values.
After parsing a complete brief, hand back to the triage agent with your results.
"""

RESEARCH_INSTRUCTIONS = """You are a Research Agent for a retail marketing system.
Your role is to provide product information, market insights, and relevant data FOR MARKETING PURPOSES ONLY.
Do not provide general research, personal advice, or information unrelated to marketing content creation.

When asked about products or market data:
- Provide realistic product details (features, pricing, benefits)
- Include relevant market trends
- Suggest relevant product attributes for marketing

Return structured JSON with product and market information.
After completing research, hand back to the triage agent with your findings.
"""

TEXT_CONTENT_INSTRUCTIONS = f"""You are a Text Content Agent specializing in MARKETING COPY ONLY.
Create compelling marketing copy for retail campaigns.
Your scope is strictly limited to marketing content: ads, social posts, emails, product descriptions, taglines, and promotional materials.
Do not write general creative content, academic papers, code, or non-marketing text.

{app_settings.brand_guidelines.get_text_generation_prompt()}

Guidelines:
- Write engaging headlines and body copy
- Match the requested tone and style
- Include clear calls-to-action
- Adapt content for the specified platform (social, email, web)
- Keep content concise and impactful

Return JSON with:
- "headline": Main headline text
- "body": Body copy text
- "cta": Call to action text
- "hashtags": Relevant hashtags (for social)
- "variations": Alternative versions if requested

After generating content, you may hand off to compliance_agent for validation,
or hand back to triage_agent with your results.
"""

IMAGE_CONTENT_INSTRUCTIONS = f"""You are an Image Content Agent for MARKETING IMAGE GENERATION ONLY.
Create detailed image prompts for DALL-E based on marketing requirements.
Your scope is strictly limited to marketing visuals: product images, ads, social media graphics, and promotional materials.
Do not generate images for non-marketing purposes such as personal art, entertainment, or general creative projects.

{app_settings.brand_guidelines.get_image_generation_prompt()}

When creating image prompts:
- Describe the scene, composition, and style clearly
- Include lighting, color palette, and mood
- Specify any brand elements or product placement
- Ensure the prompt aligns with campaign objectives

Return JSON with:
- "prompt": Detailed DALL-E prompt
- "style": Visual style description
- "aspect_ratio": Recommended aspect ratio
- "notes": Additional considerations

After generating the prompt, you may hand off to compliance_agent for validation,
or hand back to triage_agent with your results.
"""

COMPLIANCE_INSTRUCTIONS = f"""You are a Compliance Agent for marketing content validation.
Review content against brand guidelines and compliance requirements.

{app_settings.brand_guidelines.get_compliance_prompt()}

Check for:
- Brand voice consistency
- Prohibited words or phrases
- Legal/regulatory compliance
- Tone appropriateness
- Factual accuracy claims

Return JSON with:
- "approved": boolean
- "violations": array of issues found, each with:
  - "severity": "info", "warning", or "error"
  - "message": description of the issue
  - "suggestion": how to fix it
- "corrected_content": corrected versions if there are errors
- "approval_status": "BLOCKED", "REVIEW_RECOMMENDED", or "APPROVED"

After validation, hand back to triage_agent with results.
"""


class ContentGenerationOrchestrator:
    """
    Orchestrates the multi-agent content generation workflow using
    Microsoft Agent Framework's HandoffBuilder.
    
    Agents:
    - Triage (coordinator) - routes requests to specialists
    - Planning (brief interpretation)
    - Research (data retrieval)
    - TextContent (copy generation)
    - ImageContent (image creation)
    - Compliance (validation)
    """
    
    def __init__(self):
        self._chat_client: Optional[AzureOpenAIChatClient] = None
        self._agents: dict = {}
        self._workflow = None
        self._initialized = False
    
    def _get_chat_client(self) -> AzureOpenAIChatClient:
        """Get or create the Azure OpenAI chat client."""
        if self._chat_client is None:
            endpoint = app_settings.azure_openai.endpoint
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")
            
            # Use DefaultAzureCredential for RBAC authentication
            logger.info("Using DefaultAzureCredential for Azure OpenAI")
            self._chat_client = AzureOpenAIChatClient(
                endpoint=endpoint,
                deployment_name=app_settings.azure_openai.gpt_model,
                api_version=app_settings.azure_openai.api_version,
                credential=DefaultAzureCredential(),
            )
        return self._chat_client
    
    def initialize(self) -> None:
        """Initialize all agents and build the handoff workflow."""
        if self._initialized:
            return
        
        logger.info("Initializing Content Generation Orchestrator with Agent Framework...")
        
        # Get the chat client
        chat_client = self._get_chat_client()
        
        # Create all agents
        triage_agent = chat_client.create_agent(
            name="triage_agent",
            instructions=TRIAGE_INSTRUCTIONS,
        )
        
        planning_agent = chat_client.create_agent(
            name="planning_agent",
            instructions=PLANNING_INSTRUCTIONS,
        )
        
        research_agent = chat_client.create_agent(
            name="research_agent",
            instructions=RESEARCH_INSTRUCTIONS,
        )
        
        text_content_agent = chat_client.create_agent(
            name="text_content_agent",
            instructions=TEXT_CONTENT_INSTRUCTIONS,
        )
        
        image_content_agent = chat_client.create_agent(
            name="image_content_agent",
            instructions=IMAGE_CONTENT_INSTRUCTIONS,
        )
        
        compliance_agent = chat_client.create_agent(
            name="compliance_agent",
            instructions=COMPLIANCE_INSTRUCTIONS,
        )
        
        # Store agents for direct access
        self._agents = {
            "triage": triage_agent,
            "planning": planning_agent,
            "research": research_agent,
            "text_content": text_content_agent,
            "image_content": image_content_agent,
            "compliance": compliance_agent,
        }
        
        # Build the handoff workflow
        # Triage can route to all specialists
        # Specialists hand back to triage after completing their task
        # Content agents can also hand off to compliance for validation
        self._workflow = (
            HandoffBuilder(
                name="content_generation_workflow",
            )
            .participants([
                triage_agent,
                planning_agent,
                research_agent,
                text_content_agent,
                image_content_agent,
                compliance_agent,
            ])
            .set_coordinator(triage_agent)
            # Triage can hand off to all specialists
            .add_handoff(triage_agent, [
                planning_agent, 
                research_agent, 
                text_content_agent, 
                image_content_agent, 
                compliance_agent
            ])
            # All specialists can hand back to triage
            .add_handoff(planning_agent, [triage_agent])
            .add_handoff(research_agent, [triage_agent])
            # Content agents can request compliance check
            .add_handoff(text_content_agent, [compliance_agent, triage_agent])
            .add_handoff(image_content_agent, [compliance_agent, triage_agent])
            # Compliance can hand back to content agents for corrections or to triage
            .add_handoff(compliance_agent, [text_content_agent, image_content_agent, triage_agent])
            .with_termination_condition(
                # Terminate after 10 user messages to prevent infinite loops
                lambda conv: sum(1 for msg in conv if msg.role.value == "user") >= 10
            )
            .build()
        )
        
        self._initialized = True
        logger.info("Content Generation Orchestrator initialized successfully with Agent Framework")
    
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: Optional[dict] = None
    ) -> AsyncIterator[dict]:
        """
        Process a user message through the orchestrated workflow.
        
        Uses the Agent Framework's HandoffBuilder workflow to coordinate
        between specialized agents.
        
        Args:
            message: The user's input message
            conversation_id: Unique identifier for the conversation
            context: Optional context (previous messages, user preferences)
        
        Yields:
            dict: Response chunks with agent responses and status updates
        """
        if not self._initialized:
            self.initialize()
        
        logger.info(f"Processing message for conversation {conversation_id}")
        
        # Prepare the input with context
        full_input = message
        if context:
            full_input = f"Context:\n{json.dumps(context, indent=2)}\n\nUser Message:\n{message}"
        
        try:
            # Collect events from the workflow stream
            events = []
            async for event in self._workflow.run_stream(full_input):
                events.append(event)
                
                # Handle different event types from the workflow
                if isinstance(event, WorkflowStatusEvent):
                    yield {
                        "type": "status",
                        "content": event.state.name,
                        "is_final": False,
                        "metadata": {"conversation_id": conversation_id}
                    }
                
                elif isinstance(event, RequestInfoEvent):
                    # Workflow is requesting user input
                    if isinstance(event.data, HandoffUserInputRequest):
                        # Extract conversation history
                        conversation_text = "\n".join([
                            f"{msg.author_name or msg.role.value}: {msg.text}"
                            for msg in event.data.conversation
                        ])
                        yield {
                            "type": "agent_response",
                            "agent": event.data.conversation[-1].author_name if event.data.conversation else "unknown",
                            "content": event.data.conversation[-1].text if event.data.conversation else "",
                            "conversation_history": conversation_text,
                            "is_final": False,
                            "requires_user_input": True,
                            "request_id": event.request_id,
                            "metadata": {"conversation_id": conversation_id}
                        }
                
                elif isinstance(event, WorkflowOutputEvent):
                    # Final output from the workflow
                    conversation = cast(list[ChatMessage], event.data)
                    if isinstance(conversation, list) and conversation:
                        # Get the last assistant message as the final response
                        assistant_messages = [
                            msg for msg in conversation 
                            if msg.role.value != "user"
                        ]
                        if assistant_messages:
                            last_msg = assistant_messages[-1]
                            yield {
                                "type": "agent_response",
                                "agent": last_msg.author_name or "assistant",
                                "content": last_msg.text,
                                "is_final": True,
                                "metadata": {"conversation_id": conversation_id}
                            }
        
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            yield {
                "type": "error",
                "content": f"An error occurred: {str(e)}",
                "is_final": True,
                "metadata": {"conversation_id": conversation_id}
            }
    
    async def send_user_response(
        self,
        request_id: str,
        user_response: str,
        conversation_id: str
    ) -> AsyncIterator[dict]:
        """
        Send a user response to a pending workflow request.
        
        Args:
            request_id: The ID of the pending request
            user_response: The user's response
            conversation_id: Unique identifier for the conversation
        
        Yields:
            dict: Response chunks from continuing the workflow
        """
        if not self._initialized:
            self.initialize()
        
        try:
            responses = {request_id: user_response}
            async for event in self._workflow.send_responses_streaming(responses):
                if isinstance(event, WorkflowStatusEvent):
                    yield {
                        "type": "status",
                        "content": event.state.name,
                        "is_final": False,
                        "metadata": {"conversation_id": conversation_id}
                    }
                
                elif isinstance(event, RequestInfoEvent):
                    if isinstance(event.data, HandoffUserInputRequest):
                        yield {
                            "type": "agent_response",
                            "agent": event.data.conversation[-1].author_name if event.data.conversation else "unknown",
                            "content": event.data.conversation[-1].text if event.data.conversation else "",
                            "is_final": False,
                            "requires_user_input": True,
                            "request_id": event.request_id,
                            "metadata": {"conversation_id": conversation_id}
                        }
                
                elif isinstance(event, WorkflowOutputEvent):
                    conversation = cast(list[ChatMessage], event.data)
                    if isinstance(conversation, list) and conversation:
                        assistant_messages = [
                            msg for msg in conversation 
                            if msg.role.value != "user"
                        ]
                        if assistant_messages:
                            last_msg = assistant_messages[-1]
                            yield {
                                "type": "agent_response",
                                "agent": last_msg.author_name or "assistant",
                                "content": last_msg.text,
                                "is_final": True,
                                "metadata": {"conversation_id": conversation_id}
                            }
        
        except Exception as e:
            logger.exception(f"Error sending user response: {e}")
            yield {
                "type": "error",
                "content": f"An error occurred: {str(e)}",
                "is_final": True,
                "metadata": {"conversation_id": conversation_id}
            }
    
    async def parse_brief(
        self,
        brief_text: str
    ) -> tuple[CreativeBrief, str | None]:
        """
        Parse a free-text creative brief into structured format.
        If critical information is missing, return clarifying questions.
        
        Args:
            brief_text: Free-text creative brief from user
        
        Returns:
            tuple: (CreativeBrief, clarifying_questions_or_none)
                - If all critical fields are provided: (brief, None)
                - If critical fields are missing: (partial_brief, clarifying_questions_string)
        """
        if not self._initialized:
            self.initialize()
        
        planning_agent = self._agents["planning"]
        
        # First, analyze the brief and check for missing critical fields
        analysis_prompt = f"""
Analyze this creative brief request and determine if all critical information is provided.

**User's Request:**
{brief_text}

**Critical Fields Required:**
1. objectives - What is the campaign trying to achieve?
2. target_audience - Who is the intended audience?
3. key_message - What is the core message or value proposition?
4. deliverable - What content format is needed (e.g., email, social post, ad)?
5. tone_and_style - What is the desired tone (professional, casual, playful)?

**Your Task:**
1. Extract any information that IS explicitly provided
2. Identify which critical fields are MISSING or unclear
3. Return a JSON response in this EXACT format:

```json
{{
    "status": "complete" or "incomplete",
    "extracted_fields": {{
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
    "missing_fields": ["field1", "field2"],
    "clarifying_message": "If incomplete, a friendly message acknowledging what was provided and asking specific questions about what's missing. Reference the user's actual input. If complete, leave empty."
}}
```

**Rules:**
- Set status to "complete" only if objectives, target_audience, key_message, deliverable, AND tone_and_style are all clearly specified
- For extracted_fields, use empty string "" for any field not mentioned
- Do NOT invent or assume information that wasn't explicitly stated
- Make clarifying questions specific to the user's context (reference their product/campaign)
"""
        
        # Use the agent's run method
        response = await planning_agent.run(analysis_prompt)
        
        # Parse the analysis response
        try:
            response_text = str(response)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            analysis = json.loads(response_text)
            brief_data = analysis.get("extracted_fields", {})
            
            # Ensure all fields are strings
            for key in brief_data:
                if isinstance(brief_data[key], dict):
                    brief_data[key] = " | ".join(f"{k}: {v}" for k, v in brief_data[key].items())
                elif isinstance(brief_data[key], list):
                    brief_data[key] = ", ".join(str(item) for item in brief_data[key])
                elif brief_data[key] is None:
                    brief_data[key] = ""
                elif not isinstance(brief_data[key], str):
                    brief_data[key] = str(brief_data[key])
            
            # Ensure all required fields exist
            for field in ['overview', 'objectives', 'target_audience', 'key_message', 
                          'tone_and_style', 'deliverable', 'timelines', 'visual_guidelines', 'cta']:
                if field not in brief_data:
                    brief_data[field] = ""
            
            brief = CreativeBrief(**brief_data)
            
            # Check if we need clarifying questions
            if analysis.get("status") == "incomplete" and analysis.get("clarifying_message"):
                return (brief, analysis["clarifying_message"])
            
            return (brief, None)
            
        except Exception as e:
            logger.error(f"Failed to parse brief analysis response: {e}")
            # Fallback to basic extraction
            return (self._extract_brief_from_text(brief_text), None)
    
    def _extract_brief_from_text(self, text: str) -> CreativeBrief:
        """Extract brief fields from labeled text like 'Overview: ...'"""
        fields = {
            'overview': '',
            'objectives': '',
            'target_audience': '',
            'key_message': '',
            'tone_and_style': '',
            'deliverable': '',
            'timelines': '',
            'visual_guidelines': '',
            'cta': ''
        }
        
        # Common label variations
        label_map = {
            'overview': ['overview'],
            'objectives': ['objectives', 'objective'],
            'target_audience': ['target audience', 'target_audience', 'audience'],
            'key_message': ['key message', 'key_message', 'message'],
            'tone_and_style': ['tone & style', 'tone and style', 'tone_and_style', 'tone', 'style'],
            'deliverable': ['deliverable', 'deliverables'],
            'timelines': ['timeline', 'timelines', 'timing'],
            'visual_guidelines': ['visual guidelines', 'visual_guidelines', 'visuals'],
            'cta': ['call to action', 'cta', 'call-to-action']
        }
        
        lines = text.strip().split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a label
            found_label = False
            for field, labels in label_map.items():
                for label in labels:
                    if line.lower().startswith(label + ':'):
                        current_field = field
                        # Get the value after the colon
                        value = line[len(label) + 1:].strip()
                        fields[field] = value
                        found_label = True
                        break
                if found_label:
                    break
            
            # If no label found and we have a current field, append to it
            if not found_label and current_field:
                fields[current_field] += ' ' + line
        
        # If no fields were extracted, put everything in overview
        if not any(fields.values()):
            fields['overview'] = text
        
        return CreativeBrief(**fields)
    
    async def select_products(
        self,
        request_text: str,
        current_products: list = None,
        available_products: list = None
    ) -> dict:
        """
        Select or modify product selection via natural language.
        
        Args:
            request_text: User's natural language request for product selection
            current_products: Currently selected products (for modifications)
            available_products: List of available products to choose from
        
        Returns:
            dict: Selected products and assistant message
        """
        if not self._initialized:
            self.initialize()
        
        research_agent = self._agents["research"]
        
        # Build context for the agent
        current_skus = [p.get('sku', '') for p in (current_products or [])] if current_products else []
        
        select_prompt = f"""
You are helping a user select products for a marketing campaign.

User request: {request_text}

Currently selected products: {json.dumps(current_products or [], indent=2)}

Available products catalog:
{json.dumps(available_products or [], indent=2)}

Based on the user's request, determine which products should be selected.
The user might want to:
- Add specific products by name
- Remove products from selection
- Replace the entire selection
- Search for products matching criteria (color, category, use case)

Return ONLY a valid JSON object with:
{{
    "selected_products": [<list of complete product objects that should be selected>],
    "action": "<add|remove|replace|search>",
    "message": "<brief explanation of what was done>"
}}

Important:
- For "add" action: include both current products AND new products
- For "remove" action: include current products MINUS the ones to remove
- For "replace" action: include only the new products
- For "search" action: include products matching the search criteria
- Return complete product objects from the available catalog, not just names
"""
        
        try:
            response = await research_agent.run(select_prompt)
            response_text = str(response)
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return {
                "products": result.get("selected_products", []),
                "action": result.get("action", "search"),
                "message": result.get("message", "Products updated based on your request.")
            }
        except Exception as e:
            logger.error(f"Failed to process product selection: {e}")
            # Return current products unchanged with error message
            return {
                "products": current_products or [],
                "action": "error",
                "message": f"I had trouble understanding that request. Please try again with something like 'select SnowVeil paint' or 'show me exterior paints'."
            }

    async def generate_content(
        self,
        brief: CreativeBrief,
        products: list = None,
        generate_images: bool = True
    ) -> dict:
        """
        Generate complete content package from a confirmed creative brief.
        
        Args:
            brief: Confirmed creative brief
            products: List of products to feature
            generate_images: Whether to generate images
        
        Returns:
            dict: Generated content with compliance results
        """
        if not self._initialized:
            self.initialize()
        
        results = {
            "text_content": None,
            "image_prompt": None,
            "compliance": None,
            "violations": [],
            "requires_modification": False
        }
        
        # Build the generation request for text content
        text_request = f"""
Generate marketing content based on this creative brief:

Overview: {brief.overview}
Objectives: {brief.objectives}
Target Audience: {brief.target_audience}
Key Message: {brief.key_message}
Tone and Style: {brief.tone_and_style}
Deliverable: {brief.deliverable}
CTA: {brief.cta}

Products to feature: {json.dumps(products or [])}
"""
        
        try:
            # Generate text content
            text_response = await self._agents["text_content"].run(text_request)
            results["text_content"] = str(text_response)
            
            # Generate image prompt if requested
            if generate_images:
                # Build product context for image generation
                # Prefer detailed image_description if available (generated by GPT-4 Vision)
                product_context = ""
                detailed_image_context = ""
                if products:
                    product_details = []
                    image_descriptions = []
                    for p in products[:3]:  # Limit to 3 products for prompt
                        name = p.get('product_name', 'Product')
                        desc = p.get('description', p.get('marketing_description', ''))
                        tags = p.get('tags', '')
                        product_details.append(f"- {name}: {desc} (Tags: {tags})")
                        
                        # Include detailed image description if available
                        img_desc = p.get('image_description')
                        if img_desc:
                            image_descriptions.append(f"### {name} - Detailed Visual Description:\n{img_desc}")
                    
                    product_context = "\n".join(product_details)
                    if image_descriptions:
                        detailed_image_context = "\n\n".join(image_descriptions)
                
                image_request = f"""
Create an image generation prompt for this marketing campaign:

Visual Guidelines: {brief.visual_guidelines}
Key Message: {brief.key_message}
Tone and Style: {brief.tone_and_style}

PRODUCTS TO FEATURE (use these descriptions to accurately represent the products):
{product_context if product_context else 'No specific products - create a brand lifestyle image'}

{f'''DETAILED VISUAL DESCRIPTIONS OF PRODUCT COLORS (use these for accurate color reproduction):
{detailed_image_context}''' if detailed_image_context else ''}

Text content context: {str(text_response)[:500] if text_response else 'N/A'}

IMPORTANT: The generated image should visually represent the featured products using their descriptions.
For paint products, show the paint colors in context (on walls, swatches, or room settings).
Use the detailed visual descriptions above to ensure accurate color reproduction in the generated image.
"""
                image_response = await self._agents["image_content"].run(image_request)
                results["image_prompt"] = str(image_response)
                
                # Extract clean prompt from the response and generate actual image
                try:
                    from backend.agents.image_content_agent import generate_dalle_image
                    
                    # Try to extract a clean prompt from the agent response
                    prompt_text = str(image_response)
                    
                    # If response is JSON, extract the prompt field
                    if '{' in prompt_text:
                        try:
                            prompt_data = json.loads(prompt_text)
                            if isinstance(prompt_data, dict):
                                prompt_text = prompt_data.get('prompt', prompt_data.get('image_prompt', prompt_text))
                        except json.JSONDecodeError:
                            # Try to extract JSON from markdown code blocks
                            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', prompt_text, re.DOTALL)
                            if json_match:
                                try:
                                    prompt_data = json.loads(json_match.group(1))
                                    prompt_text = prompt_data.get('prompt', prompt_data.get('image_prompt', prompt_text))
                                except:
                                    pass
                    
                    # Build product description for DALL-E context
                    # Include detailed image descriptions if available for better color accuracy
                    product_description = detailed_image_context if detailed_image_context else product_context
                    
                    # Generate the actual image using DALL-E
                    logger.info(f"Generating DALL-E image with prompt: {prompt_text[:200]}...")
                    image_result = await generate_dalle_image(
                        prompt=prompt_text,
                        product_description=product_description,
                        scene_description=brief.visual_guidelines
                    )
                    
                    if image_result.get("success"):
                        image_base64 = image_result.get("image_base64")
                        results["image_revised_prompt"] = image_result.get("revised_prompt")
                        logger.info("DALL-E image generated successfully")
                        
                        # Save to blob storage immediately to avoid returning huge base64
                        # This prevents timeout issues with large responses
                        try:
                            from backend.services.blob_service import BlobStorageService
                            import os
                            from datetime import datetime
                            
                            blob_service = BlobStorageService()
                            # Generate a unique conversation-like ID for this generation
                            gen_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                            logger.info(f"Saving image to blob storage (size: {len(image_base64)} bytes)...")
                            
                            blob_url = await blob_service.save_generated_image(
                                conversation_id=f"gen_{gen_id}",
                                image_base64=image_base64
                            )
                            
                            if blob_url:
                                # Store the blob URL - will be converted to proxy URL by app.py
                                results["image_blob_url"] = blob_url
                                logger.info(f"Image saved to blob: {blob_url}")
                            else:
                                # Fallback to base64 if blob save fails
                                results["image_base64"] = image_base64
                                logger.warning("Blob save returned None, falling back to base64")
                        except Exception as blob_error:
                            logger.warning(f"Failed to save to blob, falling back to base64: {blob_error}")
                            results["image_base64"] = image_base64
                    else:
                        logger.warning(f"DALL-E image generation failed: {image_result.get('error')}")
                        results["image_error"] = image_result.get("error")
                        
                except Exception as img_error:
                    logger.exception(f"Error generating DALL-E image: {img_error}")
                    results["image_error"] = str(img_error)
            
            # Run compliance check
            compliance_request = f"""
Review this marketing content for compliance:

TEXT CONTENT:
{results["text_content"]}

IMAGE PROMPT:
{results.get('image_prompt', 'N/A')}

Check against brand guidelines and flag any issues.
"""
            compliance_response = await self._agents["compliance"].run(compliance_request)
            results["compliance"] = str(compliance_response)
            
            # Try to parse compliance violations
            try:
                compliance_data = json.loads(str(compliance_response))
                violations = compliance_data.get("violations", [])
                # Store violations as dicts for JSON serialization
                results["violations"] = [
                    {
                        "severity": v.get("severity", "warning"),
                        "message": v.get("message", v.get("description", "")),
                        "suggestion": v.get("suggestion", ""),
                        "field": v.get("field", v.get("location"))
                    }
                    for v in violations
                    if v.get("message") or v.get("description")  # Only include if has message
                ]
                results["requires_modification"] = any(
                    v.get("severity") == "error"
                    for v in results["violations"]
                )
            except (json.JSONDecodeError, KeyError):
                pass
                
        except Exception as e:
            logger.exception(f"Error generating content: {e}")
            results["error"] = str(e)
        
        # Log results summary before returning
        logger.info(f"Orchestrator returning results with keys: {list(results.keys())}")
        has_image = bool(results.get("image_base64"))
        image_size = len(results.get("image_base64", "")) if has_image else 0
        logger.info(f"Orchestrator results: has_image={has_image}, image_size={image_size}, has_error={bool(results.get('error'))}")
        
        return results


# Singleton instance
_orchestrator: Optional[ContentGenerationOrchestrator] = None


def get_orchestrator() -> ContentGenerationOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ContentGenerationOrchestrator()
        _orchestrator.initialize()
    return _orchestrator
