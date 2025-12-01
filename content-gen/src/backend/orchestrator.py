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

import asyncio
import json
import logging
import re
from typing import Any, AsyncIterator, Optional, cast
from collections.abc import AsyncIterable

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
Your role is to understand user requests and route them to the appropriate specialist agent.

Analyze the user's message and determine what they need:
- Creative brief interpretation → hand off to planning_agent
- Product data lookup → hand off to research_agent  
- Text content creation → hand off to text_content_agent
- Image creation → hand off to image_content_agent
- Content validation → hand off to compliance_agent

When you identify the need, use the appropriate handoff tool to transfer to the specialist.
If the request is unclear, ask clarifying questions before handing off.
After receiving results from specialists, summarize them for the user.

{app_settings.brand_guidelines.get_compliance_prompt()}
"""

PLANNING_INSTRUCTIONS = """You are a Planning Agent specializing in creative brief interpretation.
Parse user-provided creative briefs and extract structured information.

When given a creative brief, extract and return a JSON object with:
- overview: Campaign summary
- objectives: What the campaign aims to achieve
- target_audience: Who the content is for
- key_message: Core message to communicate
- tone_and_style: Voice and aesthetic direction
- deliverable: Expected outputs (social posts, ads, etc.)
- timelines: Any deadline information
- visual_guidelines: Visual style requirements
- cta: Call to action

After parsing, hand back to the triage agent with your results.
"""

RESEARCH_INSTRUCTIONS = """You are a Research Agent for a retail marketing system.
Your role is to provide product information, market insights, and relevant data.

When asked about products or market data:
- Provide realistic product details (features, pricing, benefits)
- Include relevant market trends
- Suggest relevant product attributes for marketing

Return structured JSON with product and market information.
After completing research, hand back to the triage agent with your findings.
"""

TEXT_CONTENT_INSTRUCTIONS = f"""You are a Text Content Agent specializing in marketing copy.
Create compelling marketing copy for retail campaigns.

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

IMAGE_CONTENT_INSTRUCTIONS = f"""You are an Image Content Agent for marketing image generation.
Create detailed image prompts for DALL-E based on marketing requirements.

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
                participants=[
                    triage_agent,
                    planning_agent,
                    research_agent,
                    text_content_agent,
                    image_content_agent,
                    compliance_agent,
                ],
            )
            .set_coordinator("triage_agent")
            # Triage can hand off to all specialists
            .add_handoff("triage_agent", [
                "planning_agent", 
                "research_agent", 
                "text_content_agent", 
                "image_content_agent", 
                "compliance_agent"
            ])
            # All specialists can hand back to triage
            .add_handoff("planning_agent", ["triage_agent"])
            .add_handoff("research_agent", ["triage_agent"])
            # Content agents can request compliance check
            .add_handoff("text_content_agent", ["compliance_agent", "triage_agent"])
            .add_handoff("image_content_agent", ["compliance_agent", "triage_agent"])
            # Compliance can hand back to content agents for corrections or to triage
            .add_handoff("compliance_agent", ["text_content_agent", "image_content_agent", "triage_agent"])
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
    ) -> CreativeBrief:
        """
        Parse a free-text creative brief into structured format.
        
        Args:
            brief_text: Free-text creative brief from user
        
        Returns:
            CreativeBrief: Parsed and structured creative brief
        """
        if not self._initialized:
            self.initialize()
        
        planning_agent = self._agents["planning"]
        
        parse_prompt = f"""
Parse the following creative brief into the structured JSON format:

{brief_text}

Return ONLY a valid JSON object with these fields:
- overview
- objectives
- target_audience
- key_message
- tone_and_style
- deliverable
- timelines
- visual_guidelines
- cta
"""
        
        # Use the agent's run method (async in Agent Framework)
        response = await planning_agent.run(parse_prompt)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            response_text = str(response)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            brief_data = json.loads(response_text)
            
            # Ensure all fields are strings (agent might return dicts for some fields)
            for key in brief_data:
                if isinstance(brief_data[key], dict):
                    # Convert dict to formatted string
                    brief_data[key] = " | ".join(f"{k}: {v}" for k, v in brief_data[key].items())
                elif isinstance(brief_data[key], list):
                    # Convert list to comma-separated string
                    brief_data[key] = ", ".join(str(item) for item in brief_data[key])
                elif brief_data[key] is None:
                    brief_data[key] = ""
                elif not isinstance(brief_data[key], str):
                    brief_data[key] = str(brief_data[key])
            
            return CreativeBrief(**brief_data)
        except Exception as e:
            logger.error(f"Failed to parse brief response: {e}")
            # Try to extract fields manually from the input text
            return self._extract_brief_from_text(brief_text)
    
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
                image_request = f"""
Create an image generation prompt for this campaign:

Visual Guidelines: {brief.visual_guidelines}
Key Message: {brief.key_message}
Tone and Style: {brief.tone_and_style}

Text content context: {str(text_response)[:500] if text_response else 'N/A'}
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
                    
                    # Generate the actual image using DALL-E
                    logger.info(f"Generating DALL-E image with prompt: {prompt_text[:200]}...")
                    image_result = await generate_dalle_image(
                        prompt=prompt_text,
                        scene_description=brief.visual_guidelines
                    )
                    
                    if image_result.get("success"):
                        results["image_base64"] = image_result.get("image_base64")
                        results["image_revised_prompt"] = image_result.get("revised_prompt")
                        logger.info("DALL-E image generated successfully")
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
