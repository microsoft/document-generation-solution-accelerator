# Standard library imports
import asyncio
import json
import logging
import os
import random
import re
import requests
import uuid
from typing import Dict, Any, AsyncGenerator

# Third-party imports
from quart import (Blueprint, Quart, jsonify, make_response, render_template,
                   request, send_from_directory)
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from azure.ai.projects.aio import AIProjectClient
from agent_framework_azure_ai import AzureAIClient
from agent_framework import ChatAgent
from cachetools import TTLCache

# First-party/Local imports
from backend.helpers.azure_credential_utils import get_azure_credential, get_azure_credential_async
from backend.auth.auth_utils import get_authenticated_user_details
from backend.history.cosmosdbservice import CosmosConversationClient
from backend.settings import app_settings
from backend.utils import (ChatType, format_as_ndjson,
                           format_non_streaming_response,
                           format_stream_response, configure_logging)
from event_utils import track_event_if_configured

bp = Blueprint("routes", __name__, static_folder="static", template_folder="static")

# Configure logging based on environment variables
configure_logging(app_settings.logging)

# Check if the Application Insights Instrumentation Key is set in the environment variables
instrumentation_key = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if instrumentation_key:
    # Configure Application Insights if the Instrumentation Key is found
    configure_azure_monitor(connection_string=instrumentation_key)
    logging.info("Application Insights configured with the provided Instrumentation Key")
else:
    # Log a warning if the Instrumentation Key is not found
    logging.warning("No Application Insights Instrumentation Key found. Skipping configuration")


def create_app():
    """
    Create and configure the Quart application instance.
    
    Returns:
        Quart: Configured Quart application instance
    """
    app = Quart(__name__)
    app.register_blueprint(bp)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config['PROVIDE_AUTOMATIC_OPTIONS'] = True

    @app.after_serving
    async def shutdown():
        """
        Perform any cleanup tasks after the app stops serving requests.
        """
        print("Shutting down the application...", flush=True)
        try:
            track_event_if_configured("ApplicationShutdown", {"status": "success"})
        except Exception as e:
            logging.exception("Error during application shutdown")
            track_event_if_configured("ApplicationShutdownError", {"status": "error"})
            raise e

    return app


@bp.route("/")
async def index():
    """
    Render the main index page.
    
    Returns:
        Rendered HTML template for the index page
    """
    return await render_template(
        "index.html", title=app_settings.ui.title, favicon=app_settings.ui.favicon
    )


@bp.route("/favicon.ico")
async def favicon():
    """
    Serve the favicon.ico file.
    
    Returns:
        Static favicon file
    """
    return await bp.send_static_file("favicon.ico")


@bp.route("/assets/<path:path>")
async def assets(path):
    """
    Serve static assets from the assets directory.
    
    Args:
        path: Path to the asset file
        
    Returns:
        Static asset file
    """
    return await send_from_directory("static/assets", path)


# Debug settings are now handled by the logging configuration above

USER_AGENT = "GitHubSampleWebApp/AsyncAzureOpenAI/1.0.0"


# Frontend Settings via Environment Variables
frontend_settings = {
    "auth_enabled": app_settings.base_settings.auth_enabled,
    "feedback_enabled": (
        app_settings.chat_history and app_settings.chat_history.enable_feedback
    ),
    "ui": {
        "title": app_settings.ui.title,
        "logo": app_settings.ui.logo,
        "chat_logo": app_settings.ui.chat_logo or app_settings.ui.logo,
        "chat_title": app_settings.ui.chat_title,
        "chat_description": app_settings.ui.chat_description,
        "show_share_button": app_settings.ui.show_share_button,
    },
    "sanitize_answer": app_settings.base_settings.sanitize_answer,
}


# Enable Microsoft Defender for Cloud Integration
MS_DEFENDER_ENABLED = os.environ.get("MS_DEFENDER_ENABLED", "true").lower() == "true"


class ExpCache(TTLCache):
    """Extended TTLCache that deletes Azure AI agent threads when items expire."""

    def __init__(self, *args, **kwargs):
        """Initialize cache without creating persistent client connections."""
        super().__init__(*args, **kwargs)

    def expire(self, time=None):
        """Remove expired items and delete associated Azure AI threads."""
        items = super().expire(time)
        for key, thread_conversation_id in items:
            try:
                # Create task for async deletion with proper session management
                asyncio.create_task(self._delete_thread_async(thread_conversation_id))
                logging.info("Scheduled thread deletion: %s", thread_conversation_id)
            except Exception as e:
                logging.error("Failed to schedule thread deletion for key %s: %s", key, e)
        return items

    def popitem(self):
        """Remove item using LRU eviction and delete associated Azure AI thread."""
        key, thread_conversation_id = super().popitem()
        try:
            # Create task for async deletion with proper session management
            asyncio.create_task(self._delete_thread_async(thread_conversation_id))
            logging.info("Scheduled thread deletion (LRU evict): %s", thread_conversation_id)
        except Exception as e:
            logging.error("Failed to schedule thread deletion for key %s (LRU evict): %s", key, e)
        return key, thread_conversation_id

    async def _delete_thread_async(self, thread_conversation_id: str):
        """Asynchronously delete a thread using a properly managed Azure AI Project Client."""
        credential = None
        try:
            if thread_conversation_id:
                # Get credential and use async context managers to ensure proper cleanup
                credential = await get_azure_credential_async(client_id=app_settings.base_settings.azure_client_id)
                async with AIProjectClient(
                    endpoint=app_settings.azure_ai.agent_endpoint,
                    credential=credential
                ) as project_client:
                    openai_client = project_client.get_openai_client()
                    await openai_client.conversations.delete(conversation_id=thread_conversation_id)
                    logging.info("Thread deleted successfully: %s", thread_conversation_id)
        except Exception as e:
            logging.error("Failed to delete thread %s: %s", thread_conversation_id, e)
        finally:
            # Close credential to prevent unclosed client session warnings
            if credential is not None:
                await credential.close()


thread_cache = None


def get_thread_cache():
    """Get or create the global thread cache."""
    global thread_cache
    if thread_cache is None:
        thread_cache = ExpCache(maxsize=1000, ttl=3600.0)
    return thread_cache


def init_cosmosdb_client():
    """
    Initialize and configure the CosmosDB conversation client.
    
    Returns:
        CosmosConversationClient: Configured CosmosDB client or None if not configured
        
    Raises:
        Exception: If there's an error during CosmosDB initialization
    """
    cosmos_conversation_client = None
    if app_settings.chat_history:
        try:
            cosmos_endpoint = (
                f"https://{app_settings.chat_history.account}.documents.azure.com:443/"
            )

            if not app_settings.chat_history.account_key:
                credential = get_azure_credential(client_id=app_settings.base_settings.azure_client_id)
            else:
                credential = app_settings.chat_history.account_key

            cosmos_conversation_client = CosmosConversationClient(
                cosmosdb_endpoint=cosmos_endpoint,
                credential=credential,
                database_name=app_settings.chat_history.database,
                container_name=app_settings.chat_history.conversations_container,
                enable_message_feedback=app_settings.chat_history.enable_feedback,
            )
        except Exception as e:
            logging.exception("Exception in CosmosDB initialization", e)
            span = trace.get_current_span()
            if span is not None:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
            cosmos_conversation_client = None
            raise e
    else:
        logging.debug("CosmosDB not configured")

    return cosmos_conversation_client


# Conversion of citation markers
def convert_citation_markers(text, doc_mapping):
    """
    Convert citation markers in text to numbered citations.
    
    Args:
        text: Text containing citation markers
        doc_mapping: Dictionary mapping citation keys to citation numbers
        
    Returns:
        str: Text with converted citation markers
    """
    def replace_marker(match):
        key = match.group(1)
        if key not in doc_mapping:
            doc_mapping[key] = f"[{len(doc_mapping) + 1}]"
        return doc_mapping[key]

    return re.sub(r'【(\d+:\d+)†source】', replace_marker, text)


async def send_chat_request(request_body, request_headers) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Send a chat request to the appropriate agent based on chat type.
    
    Args:
        request_body: Request body containing query and chat type
        request_headers: HTTP request headers
        
    Yields:
        Dict[str, Any]: Response chunks containing answer and citations
        
    Raises:
        ValueError: If agent name is not configured
        Exception: If there's an error during chat request processing
    """
    # Get the user query directly from request body
    query = request_body.get("query", "")
    
    if not query:
        query = "Please provide a query."
    
    # Get conversation_id for thread management
    conversation_id = request_body.get("history_metadata", {}).get("conversation_id", None)
    if not conversation_id:
        # Fallback: generate a unique conversation ID if not provided
        conversation_id = str(uuid.uuid4())
        logging.warning("No conversation_id provided, generated new one: %s", conversation_id)
    
    track_event_if_configured("ChatRequestReceived", {
        "conversation_id": conversation_id,
        "query_length": len(query)
    })

    try:
        track_event_if_configured("Foundry_sdk_for_response", {"status": "success"})
        answer: Dict[str, Any] = {"answer": "", "citations": []}
        doc_mapping = {}

        # Browse
        if request_body["chat_type"] == "browse":
            # Get browse agent name and create AzureAIClient
            browse_agent_name = app_settings.azure_ai.agent_name_browse
            if not browse_agent_name:
                raise ValueError("Browse agent name not configured in settings")

            async with (
                await get_azure_credential_async(client_id=app_settings.base_settings.azure_client_id) as credential,
                AIProjectClient(endpoint=app_settings.azure_ai.agent_endpoint, credential=credential) as project_client,
            ):
                chat_client = AzureAIClient(
                    project_client=project_client,
                    agent_name=browse_agent_name,
                    use_latest_version=True,
                )

                # Use ChatAgent with streaming or non-streaming
                async with ChatAgent(
                    chat_client=chat_client,
                    tool_choice="auto",  # Let agent decide when to use Azure AI Search
                    store=True,
                ) as chat_agent:
                    # Thread management with TTL cache
                    thread_conversation_id = None
                    cache = get_thread_cache()
                    thread_conversation_id = cache.get(conversation_id, None)
                    
                    if thread_conversation_id:
                        thread = chat_agent.get_new_thread(service_thread_id=thread_conversation_id)
                    else:
                        # Create a new conversation thread
                        openai_client = project_client.get_openai_client()
                        conversation = await openai_client.conversations.create()
                        thread_conversation_id = conversation.id
                        thread = chat_agent.get_new_thread(service_thread_id=thread_conversation_id)

                    if app_settings.azure_openai.stream:
                        # Stream response
                        async for chunk in chat_agent.run_stream(messages=query, thread=thread):
                            # Extract text from chunk
                            if hasattr(chunk, 'text') and chunk.text:
                                delta_text = chunk.text
                                answer["answer"] += delta_text

                                # Check if citation markers are present
                                has_citation_markers = bool(re.search(r'【(\d+:\d+)†source】', delta_text))
                                if has_citation_markers:
                                    yield {
                                        "answer": convert_citation_markers(delta_text, doc_mapping),
                                        "citations": json.dumps(answer["citations"])
                                    }
                                else:
                                    yield {
                                        "answer": delta_text
                                    }

                            # # Collect citations from annotations
                            # if hasattr(chunk, 'contents') and chunk.contents:
                            #     for content in chunk.contents:
                            #         if hasattr(content, 'annotations') and content.annotations:
                            #             for annotation in content.annotations:
                            #                 if hasattr(annotation, 'url') and hasattr(annotation, 'title'):
                            #                     if annotation.url not in [c["url"] for c in answer["citations"]]:
                            #                         answer["citations"].append({
                            #                             "title": annotation.title,
                            #                             "url": annotation.url
                            #                         })

                        # Final citation update if needed
                        has_final_citation_markers = bool(re.search(r'【(\d+:\d+)†source】', answer["answer"]))
                        if has_final_citation_markers:
                            yield {
                                "citations": json.dumps(answer["citations"])
                            }
                        
                        # Cache the thread_conversation_id for future use
                        cache[conversation_id] = thread_conversation_id
                    else:
                        # Non-streaming response
                        result = await chat_agent.run(messages=query, thread=thread)

                        # Extract text from result
                        if hasattr(result, 'text'):
                            response_text = result.text
                        else:
                            response_text = str(result) if result is not None else ""

                        answer["answer"] = response_text

                        # # Collect citations from annotations
                        # if hasattr(result, 'contents') and result.contents:
                        #     for content in result.contents:
                        #         if hasattr(content, 'annotations') and content.annotations:
                        #             for annotation in content.annotations:
                        #                 if hasattr(annotation, 'url') and hasattr(annotation, 'title'):
                        #                     if annotation.url not in [c["url"] for c in answer["citations"]]:
                        #                         answer["citations"].append({
                        #                             "title": annotation.title,
                        #                             "url": annotation.url
                        #                         })

                        # Check if citation markers are present
                        has_citation_markers = bool(re.search(r'【(\d+:\d+)†source】', response_text))
                        if has_citation_markers:
                            yield {
                                "answer": convert_citation_markers(response_text, doc_mapping),
                                "citations": json.dumps(answer["citations"])
                            }
                        else:
                            yield {
                                "answer": response_text,
                                "citations": json.dumps(answer["citations"])
                            }
                        
                        # Cache the thread_conversation_id for future use
                        cache[conversation_id] = thread_conversation_id

        # Generate Template
        else:
            # Get template agent name and create AzureAIClient
            template_agent_name = app_settings.azure_ai.agent_name_template
            if not template_agent_name:
                raise ValueError("Template agent name not configured in settings")

            async with (
                await get_azure_credential_async(client_id=app_settings.base_settings.azure_client_id) as credential,
                AIProjectClient(endpoint=app_settings.azure_ai.agent_endpoint, credential=credential) as project_client,
            ):
                chat_client = AzureAIClient(
                    project_client=project_client,
                    agent_name=template_agent_name,
                    use_latest_version=True,
                )

                # Use ChatAgent for template generation (non-streaming only for template)
                async with ChatAgent(
                    chat_client=chat_client,
                    tool_choice="auto",  # Let agent decide when to use Azure AI Search
                    store=True,
                ) as chat_agent:
                    # Thread management with TTL cache
                    thread_conversation_id = None
                    cache = get_thread_cache()
                    thread_conversation_id = cache.get(conversation_id, None)
                    
                    if thread_conversation_id:
                        thread = chat_agent.get_new_thread(service_thread_id=thread_conversation_id)
                    else:
                        # Create a new conversation thread
                        openai_client = project_client.get_openai_client()
                        conversation = await openai_client.conversations.create()
                        thread_conversation_id = conversation.id
                        thread = chat_agent.get_new_thread(service_thread_id=thread_conversation_id)
                    
                    result = await chat_agent.run(messages=query, thread=thread)

                    # Extract text from result
                    if hasattr(result, 'text'):
                        response_text = result.text
                    else:
                        response_text = str(result) if result is not None else ""

                    # Remove citation markers from template
                    response_text = re.sub(r'【(\d+:\d+)†source】', '', response_text)
                    answer["answer"] = convert_citation_markers(response_text, doc_mapping)

                    # # Collect citations from annotations (if any)
                    # if hasattr(result, 'contents') and result.contents:
                    #     for content in result.contents:
                    #         if hasattr(content, 'annotations') and content.annotations:
                    #             for annotation in content.annotations:
                    #                 if hasattr(annotation, 'url') and hasattr(annotation, 'title'):
                    #                     if annotation.url not in [c["url"] for c in answer["citations"]]:
                    #                         answer["citations"].append({
                    #                             "title": annotation.title,
                    #                             "url": annotation.url
                    #                         })

                    yield {
                        "answer": answer["answer"],
                        "citations": json.dumps(answer["citations"])
                    }
                    
                    # Cache the thread_conversation_id for future use
                    cache[conversation_id] = thread_conversation_id

    except Exception as e:
        logging.exception("Exception in send_chat_request")
        print(f"Exception in send_chat_request: {e}", flush=True)
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        
        # Clean up corrupted thread from cache on error
        try:
            cache = get_thread_cache()
            thread_conversation_id = cache.pop(conversation_id, None)
            if thread_conversation_id is not None:
                # Store corrupted thread with a unique key for later cleanup
                corrupt_key = f"{conversation_id}_corrupt_{random.randint(1000, 9999)}"
                cache[corrupt_key] = thread_conversation_id
                logging.warning("Moved corrupted thread to key: %s", corrupt_key)
        except Exception as cleanup_error:
            logging.error("Failed to cleanup thread on error: %s", cleanup_error)
        
        raise e


async def complete_chat_request(request_body, request_headers):
    """
    Complete a non-streaming chat request.
    
    Args:
        request_body: Request body containing messages and metadata
        request_headers: HTTP request headers
        
    Returns:
        Formatted non-streaming response
    """
    # response, apim_request_id = await send_chat_request(request_body, request_headers)
    response = None
    history_metadata = request_body.get("history_metadata", {})

    async for chunk in send_chat_request(request_body, request_headers):
        response = chunk  # Only the last chunk matters for non-streaming

    return format_non_streaming_response(response, history_metadata)


async def stream_chat_request(request_body, request_headers):
    """
    Stream a chat request with real-time response chunks.
    
    Args:
        request_body: Request body containing messages and metadata
        request_headers: HTTP request headers
        
    Returns:
        AsyncGenerator: Generator yielding formatted stream response chunks
    """
    track_event_if_configured("StreamChatRequestStart", {
        "has_history_metadata": "history_metadata" in request_body
    })
    # response, apim_request_id = await send_chat_request(request_body, request_headers)
    history_metadata = request_body.get("history_metadata", {})

    async def generate():
        async for chunk in send_chat_request(request_body, request_headers):
            yield format_stream_response(chunk, history_metadata)

    return generate()


async def conversation_internal(request_body, request_headers):
    """
    Internal handler for conversation requests.
    
    Args:
        request_body: Request body containing messages and chat type
        request_headers: HTTP request headers
        
    Returns:
        JSON response with conversation result or error
    """
    try:
        chat_type = (
            ChatType.BROWSE
            if not (
                request_body["chat_type"] and request_body["chat_type"] == "template"
            )
            else ChatType.TEMPLATE
        )
        track_event_if_configured("ConversationRequestReceived", {
            "chat_type": str(chat_type),
            "streaming_enabled": app_settings.azure_openai.stream
        })
        if app_settings.azure_openai.stream and chat_type == ChatType.BROWSE:
            result = await stream_chat_request(request_body, request_headers)
            response = await make_response(format_as_ndjson(result))
            response.timeout = None
            response.mimetype = "application/json-lines"
            track_event_if_configured("ConversationStreamResponsePrepared", {
                "response": response
            })
            return response
        else:
            result = await complete_chat_request(request_body, request_headers)
            track_event_if_configured("ConversationCompleteResponsePrepared", {
                "result": json.dumps(result)
            })
            return jsonify(result)

    except Exception as ex:
        logging.exception(ex)
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(ex)
            span.set_status(Status(StatusCode.ERROR, str(ex)))

        if hasattr(ex, "status_code"):
            return jsonify({"error": str(ex)}), ex.status_code
        else:
            return jsonify({"error": str(ex)}), 500


@bp.route("/conversation", methods=["POST"])
async def conversation():
    """
    Handle POST requests to the /conversation endpoint.
    
    Returns:
        JSON response with conversation result or error
    """
    if not request.is_json:
        track_event_if_configured("InvalidRequestFormat", {
            "status_code": 415,
            "detail": "Request must be JSON"
        })
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()

    return await conversation_internal(request_json, request.headers)


@bp.route("/frontend_settings", methods=["GET"])
def get_frontend_settings():
    """
    Get frontend configuration settings.
    
    Returns:
        JSON response with frontend settings or error
    """
    try:
        return jsonify(frontend_settings), 200
    except Exception as e:
        logging.exception("Exception in /frontend_settings")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


# Conversation History API #
@bp.route("/history/generate", methods=["POST"])
async def add_conversation():
    """
    Generate a new conversation and add user message to history.
    
    Returns:
        JSON response with conversation result or error
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    if not user_id:
        track_event_if_configured("UserIdNotFound", {"status_code": 400, "detail": "no user"})

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    try:
        # make sure cosmos is configured
        cosmos_conversation_client = init_cosmosdb_client()
        if not cosmos_conversation_client:
            track_event_if_configured("CosmosNotConfigured", {"error": "CosmosDB is not configured"})
            raise Exception("CosmosDB is not configured or not working")

        # Get user query from request
        query = request_json.get("query", "")
        if not query:
            track_event_if_configured("NoUserQuery", {"status_code": 400, "detail": "No user query provided"})
            raise Exception("No user query provided")

        # check for the conversation_id, if the conversation is not set, we will create a new one
        history_metadata = {}
        if not conversation_id:
            # Create title from the query
            title = await generate_title([{"role": "user", "content": query}])
            conversation_dict = await cosmos_conversation_client.create_conversation(
                user_id=user_id, title=title
            )
            conversation_id = conversation_dict["id"]
            history_metadata["title"] = title
            history_metadata["date"] = conversation_dict["createdAt"]

        # Format the user query as a message object in the "chat/completions" format
        # then write it to the conversation history in cosmos
        user_message = {"role": "user", "content": query}
        createdMessageValue = await cosmos_conversation_client.create_message(
            uuid=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_id=user_id,
            input_message=user_message,
        )

        track_event_if_configured("MessageCreated", {
            "conversation_id": conversation_id,
            "message_id": json.dumps(user_message),
            "user_id": user_id
        })
        if createdMessageValue == "Conversation not found":
            track_event_if_configured("ConversationNotFound", {"conversation_id": conversation_id})
            raise Exception(
                "Conversation not found for the given conversation ID: "
                + conversation_id
                + "."
            )

        await cosmos_conversation_client.cosmosdb_client.close()

        # Submit request to Chat Completions for response
        request_body = await request.get_json()
        history_metadata["conversation_id"] = conversation_id
        request_body["history_metadata"] = history_metadata
        track_event_if_configured("ConversationHistoryGenerated", {"conversation_id": conversation_id})
        return await conversation_internal(request_body, request.headers)

    except Exception as e:
        logging.exception("Exception in /history/generate")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/update", methods=["POST"])
async def update_conversation():
    """
    Update conversation history with assistant messages.
    
    Returns:
        JSON response with success status or error
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    if not user_id:
        track_event_if_configured("UserIdNotFound", {"status_code": 400, "detail": "no user"})

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    try:
        # make sure cosmos is configured
        cosmos_conversation_client = init_cosmosdb_client()
        if not cosmos_conversation_client:
            track_event_if_configured("CosmosNotConfigured", {"error": "CosmosDB is not configured"})
            raise Exception("CosmosDB is not configured or not working")

        # check for the conversation_id, if the conversation is not set, we will create a new one
        if not conversation_id:
            track_event_if_configured("MissingConversationId", {"error": "No conversation_id in request"})
            raise Exception("No conversation_id found")

        # Format the incoming message object in the "chat/completions" messages format
        # then write it to the conversation history in cosmos
        messages = request_json["messages"]
        if len(messages) > 0 and messages[-1]["role"] == "assistant":
            if len(messages) > 1 and messages[-2].get("role", None) == "tool":
                # write the tool message first
                await cosmos_conversation_client.create_message(
                    uuid=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    user_id=user_id,
                    input_message=messages[-2],
                )
            # write the assistant message
            await cosmos_conversation_client.create_message(
                uuid=messages[-1]["id"],
                conversation_id=conversation_id,
                user_id=user_id,
                input_message=messages[-1],
            )
        else:
            track_event_if_configured("NoAssistantMessage", {"status_code": 400, "detail": "No bot message found"})
            raise Exception("No bot messages found")

        # Submit request to Chat Completions for response
        await cosmos_conversation_client.cosmosdb_client.close()
        track_event_if_configured("ConversationHistoryUpdated", {"conversation_id": conversation_id})
        response = {"success": True}
        return jsonify(response), 200

    except Exception as e:
        logging.exception("Exception in /history/update")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/message_feedback", methods=["POST"])
async def update_message():
    """
    Update feedback for a specific message.
    
    Returns:
        JSON response with success status or error
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    cosmos_conversation_client = init_cosmosdb_client()

    # check request for message_id
    request_json = await request.get_json()
    message_id = request_json.get("message_id", None)
    message_feedback = request_json.get("message_feedback", None)
    try:
        if not message_id:
            logging.error("Missing message_id", extra={'request_json': request_json})
            track_event_if_configured("MissingMessageId", {"status_code": 400, "request_json": request_json})
            return jsonify({"error": "message_id is required"}), 400

        if not message_feedback:
            logging.error("Missing message_feedback", extra={'request_id': request_json})
            track_event_if_configured("MissingMessageFeedback", {"status_code": 400, "request_json": request_json})
            return jsonify({"error": "message_feedback is required"}), 400

        # update the message in cosmos
        updated_message = await cosmos_conversation_client.update_message_feedback(
            user_id, message_id, message_feedback
        )
        if updated_message:
            track_event_if_configured("MessageFeedbackUpdated", {
                "message_id": message_id,
                "message_feedback": message_feedback
            })
            logging.info("Message feedback updated", extra={'message_id': message_id})
            return (
                jsonify(
                    {
                        "message": f"Successfully updated message with feedback {message_feedback}",
                        "message_id": message_id,
                    }
                ),
                200,
            )
        else:
            logging.warning("Message not found or access denied", extra={'request_json': request_json})
            track_event_if_configured("MessageNotFoundOrAccessDenied", {
                "status_code": 404,
                "request_json": request_json
            })
            return (
                jsonify(
                    {
                        "error": f"Unable to update message {message_id}. "
                        "It either does not exist or the user does not have access to it."
                    }
                ),
                404,
            )

    except Exception as e:
        logging.exception("Exception in /history/message_feedback")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/delete", methods=["DELETE"])
async def delete_conversation():
    """
    Delete a conversation and all its messages.
    
    Returns:
        JSON response with success status or error
    """
    # get the user id from the request headers
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    try:
        if not conversation_id:
            track_event_if_configured("MissingConversationId", {"error": "No conversation_id in request", "request_json": request_json})
            return jsonify({"error": "conversation_id is required"}), 400

        # make sure cosmos is configured
        cosmos_conversation_client = init_cosmosdb_client()
        if not cosmos_conversation_client:
            track_event_if_configured("CosmosDBNotConfigured", {
                "user_id": user_id,
                "conversation_id": conversation_id
            })
            raise Exception("CosmosDB is not configured or not working")

        # delete the conversation messages from cosmos first
        await cosmos_conversation_client.delete_messages(conversation_id, user_id)

        # Now delete the conversation
        await cosmos_conversation_client.delete_conversation(user_id, conversation_id)

        await cosmos_conversation_client.cosmosdb_client.close()

        track_event_if_configured("ConversationDeleted", {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "status": "success"
        })

        return (
            jsonify(
                {
                    "message": "Successfully deleted conversation and messages",
                    "conversation_id": conversation_id,
                }
            ),
            200,
        )
    except Exception as e:
        logging.exception("Exception in /history/delete")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/list", methods=["GET"])
async def list_conversations():
    """
    List all conversations for the authenticated user.
    
    Returns:
        JSON response with list of conversations or error
    """
    offset = request.args.get("offset", 0)
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # make sure cosmos is configured
    cosmos_conversation_client = init_cosmosdb_client()
    if not cosmos_conversation_client:
        track_event_if_configured("CosmosDBNotConfigured", {
            "user_id": user_id,
            "error": "CosmosDB is not configured or not working"
        })
        raise Exception("CosmosDB is not configured or not working")

    # get the conversations from cosmos
    conversations = await cosmos_conversation_client.get_conversations(user_id, offset=offset, limit=25)
    await cosmos_conversation_client.cosmosdb_client.close()
    if not isinstance(conversations, list):
        track_event_if_configured("NoConversationsFound", {
            "user_id": user_id,
            "status": "No conversations found"
        })
        return jsonify({"error": f"No conversations for {user_id} were found"}), 404

    # return the conversation ids
    track_event_if_configured("ConversationsListed", {
        "user_id": user_id,
        "conversation_count": len(conversations),
        "status": "success"
    })
    return jsonify(conversations), 200


@bp.route("/history/read", methods=["POST"])
async def get_conversation():
    """
    Get a specific conversation and its messages.
    
    Returns:
        JSON response with conversation details and messages or error
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    if not conversation_id:
        track_event_if_configured("MissingConversationId", {
            "user_id": user_id,
            "error": "conversation_id is required"
        })
        return jsonify({"error": "conversation_id is required"}), 400

    # make sure cosmos is configured
    cosmos_conversation_client = init_cosmosdb_client()
    if not cosmos_conversation_client:
        track_event_if_configured("CosmosDBNotConfigured", {
            "user_id": user_id,
            "error": "CosmosDB is not configured or not working"
        })
        raise Exception("CosmosDB is not configured or not working")

    # get the conversation object and the related messages from cosmos
    conversation = await cosmos_conversation_client.get_conversation(
        user_id, conversation_id
    )
    # return the conversation id and the messages in the bot frontend format
    if not conversation:
        track_event_if_configured("ConversationNotFound", {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "error": "Conversation not found or access denied"
        })
        return (
            jsonify(
                {
                    "error": (
                        f"Conversation {conversation_id} was not found. "
                        "It either does not exist or the logged in user does not have access to it."
                    )
                }
            ),
            404,
        )

    # get the messages for the conversation from cosmos
    conversation_messages = await cosmos_conversation_client.get_messages(
        user_id, conversation_id
    )

    # format the messages in the bot frontend format
    messages = [
        {
            "id": msg["id"],
            "role": msg["role"],
            "content": msg["content"],
            "createdAt": msg["createdAt"],
            "feedback": msg.get("feedback"),
        }
        for msg in conversation_messages
    ]

    track_event_if_configured("ConversationRead", {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message_count": len(messages),
        "status": "success"
    })
    await cosmos_conversation_client.cosmosdb_client.close()
    return jsonify({"conversation_id": conversation_id, "messages": messages}), 200


@bp.route("/history/rename", methods=["POST"])
async def rename_conversation():
    """
    Rename a conversation by updating its title.
    
    Returns:
        JSON response with updated conversation or error
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    if not conversation_id:
        track_event_if_configured("MissingConversationId", {
            "user_id": user_id,
            "error": "conversation_id is required",
            "request_json": request_json
        })
        return jsonify({"error": "conversation_id is required"}), 400

    # make sure cosmos is configured
    cosmos_conversation_client = init_cosmosdb_client()
    if not cosmos_conversation_client:
        track_event_if_configured("CosmosDBNotConfigured", {
            "user_id": user_id,
            "error": "CosmosDB not configured or not working"
        })
        raise Exception("CosmosDB is not configured or not working")

    # get the conversation from cosmos
    conversation = await cosmos_conversation_client.get_conversation(
        user_id, conversation_id
    )
    if not conversation:
        track_event_if_configured("ConversationNotFoundForRename", {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "error": "Conversation not found or access denied"
        })
        return (
            jsonify(
                {
                    "error": (
                        f"Conversation {conversation_id} was not found. "
                        "It either does not exist or the logged in user does not have access to it."
                    )
                }
            ),
            404,
        )

    # update the title
    title = request_json.get("title", None)
    if not title or title.strip() == "":
        track_event_if_configured("MissingTitle", {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "error": "title is required"
        })
        return jsonify({"error": "title is required"}), 400
    conversation["title"] = title
    updated_conversation = await cosmos_conversation_client.upsert_conversation(
        conversation
    )

    await cosmos_conversation_client.cosmosdb_client.close()
    track_event_if_configured("ConversationRenamed", {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "new_title": title
    })
    return jsonify(updated_conversation), 200


@bp.route("/history/delete_all", methods=["DELETE"])
async def delete_all_conversations():
    """
    Delete all conversations and messages for the authenticated user.
    
    Returns:
        JSON response with success status or error
    """
    # get the user id from the request headers
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # get conversations for user
    try:
        # make sure cosmos is configured
        cosmos_conversation_client = init_cosmosdb_client()
        if not cosmos_conversation_client:
            track_event_if_configured("CosmosDBNotConfigured", {
                "user_id": user_id,
                "error": "CosmosDB is not configured or not working"
            })
            raise Exception("CosmosDB is not configured or not working")

        conversations = await cosmos_conversation_client.get_conversations(
            user_id, offset=0, limit=None
        )
        if not conversations:
            track_event_if_configured("NoConversationsToDelete", {
                "user_id": user_id,
                "status": "No conversations found"
            })
            return jsonify({"error": f"No conversations for {user_id} were found"}), 404

        # delete each conversation
        for conversation in conversations:
            # delete the conversation messages from cosmos first
            await cosmos_conversation_client.delete_messages(
                conversation["id"], user_id
            )

            # Now delete the conversation
            await cosmos_conversation_client.delete_conversation(
                user_id, conversation["id"]
            )
        await cosmos_conversation_client.cosmosdb_client.close()
        track_event_if_configured("AllConversationsDeleted", {
            "user_id": user_id,
            "deleted_count": len(conversations)
        })
        return (
            jsonify(
                {
                    "message": f"Successfully deleted conversation and messages for user {user_id}"
                }
            ),
            200,
        )

    except Exception as e:
        logging.exception("Exception in /history/delete_all")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/clear", methods=["POST"])
async def clear_messages():
    """
    Clear all messages in a specific conversation.
    
    Returns:
        JSON response with success status or error
    """
    # get the user id from the request headers
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    # check request for conversation_id
    request_json = await request.get_json()
    conversation_id = request_json.get("conversation_id", None)

    try:
        if not conversation_id:
            return jsonify({"error": "conversation_id is required"}), 400

        # make sure cosmos is configured
        cosmos_conversation_client = init_cosmosdb_client()
        if not cosmos_conversation_client:
            raise Exception("CosmosDB is not configured or not working")

        # delete the conversation messages from cosmos
        await cosmos_conversation_client.delete_messages(conversation_id, user_id)

        return (
            jsonify(
                {
                    "message": "Successfully deleted messages in conversation",
                    "conversation_id": conversation_id,
                }
            ),
            200,
        )
    except Exception as e:
        logging.exception("Exception in /history/clear_messages")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


@bp.route("/history/ensure", methods=["GET"])
async def ensure_cosmos():
    """
    Ensure CosmosDB is properly configured and working.
    
    Returns:
        JSON response with configuration status or error
    """
    if not app_settings.chat_history:
        return jsonify({"error": "CosmosDB is not configured"}), 404

    try:
        cosmos_conversation_client = init_cosmosdb_client()
        success, err = await cosmos_conversation_client.ensure()
        if not cosmos_conversation_client or not success:
            if err:
                track_event_if_configured("CosmosEnsureFailed", {"error": err})
                return jsonify({"error": err}), 422
            return jsonify({"error": "CosmosDB is not configured or not working"}), 500

        track_event_if_configured("CosmosEnsureSuccess", {"status": "working"})
        await cosmos_conversation_client.cosmosdb_client.close()
        return jsonify({"message": "CosmosDB is configured and working"}), 200
    except Exception as e:
        logging.exception("Exception in /history/ensure")
        cosmos_exception = str(e)
        if "Invalid credentials" in cosmos_exception:
            return jsonify({"error": cosmos_exception}), 401
        elif "Invalid CosmosDB database name" in cosmos_exception:
            return (
                jsonify(
                    {
                        "error": f"{cosmos_exception} {app_settings.chat_history.database} for account {app_settings.chat_history.account}"
                    }
                ),
                422,
            )
        elif "Invalid CosmosDB container name" in cosmos_exception:
            return (
                jsonify(
                    {
                        "error": f"{cosmos_exception}: {app_settings.chat_history.conversations_container}"
                    }
                ),
                422,
            )
        else:
            return jsonify({"error": "CosmosDB is not working"}), 500


@bp.route("/section/generate", methods=["POST"])
async def generate_section_content():
    """
    Generate content for a document section.
    
    Returns:
        JSON response with generated section content or error
    """
    request_json = await request.get_json()
    try:
        # verify that section title and section description are provided
        if "sectionTitle" not in request_json:
            track_event_if_configured("GenerateSectionFailed", {"error": "sectionTitle missing", "request_json": request_json})
            return jsonify({"error": "sectionTitle is required"}), 400

        if "sectionDescription" not in request_json:
            track_event_if_configured("GenerateSectionFailed", {"error": "sectionDescription missing", "request_json": request_json})
            return jsonify({"error": "sectionDescription is required"}), 400

        content = await get_section_content(request_json, request.headers)
        track_event_if_configured("GenerateSectionSuccess", {
            "sectionTitle": request_json["sectionTitle"]
        })
        return jsonify({"section_content": content}), 200
    except Exception as e:
        logging.exception("Exception in /section/generate")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        return jsonify({"error": str(e)}), 500


# Fetch content from Azure Search API
@bp.route("/fetch-azure-search-content", methods=["POST"])
async def fetch_azure_search_content():
    """
    Fetch content from Azure Search API using a provided URL.
    
    Returns:
        JSON response with fetched content or error
    """
    try:
        request_json = await request.get_json()
        url = request_json.get("url")
        title = request_json.get("title")

        if not url or not title:
            return jsonify({"error": "URL and title are required"}), 400

        # Get Azure AD token
        credential = get_azure_credential(client_id=app_settings.base_settings.azure_client_id)
        token = credential.get_token("https://search.azure.com/.default")
        access_token = token.token

        def fetch_content(fetch_url):
            try:
                response = requests.get(
                    fetch_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    return {"success": True, "content": content}
                else:
                    error_msg = f"Request failed with status code {response.status_code} {response.text}"
                    return {"success": False, "error": error_msg}
            except Exception as e:
                logging.exception("Error fetching content from Azure Search")
                return {"success": False, "error": f"Exception: {str(e)}"}

        result = await asyncio.to_thread(fetch_content, url)

        if result["success"]:
            return jsonify({
                "content": result["content"],
                "title": title
            }), 200
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        logging.exception("Exception in /fetch-azure-search-content")
        return jsonify({"error": str(e)}), 500


async def generate_title(conversation_messages):
    """
    Generate a conversation title using the Title Agent.

    Args:
        conversation_messages: List of conversation messages

    Returns:
        str: Generated title or fallback content
    """
    # Filter user messages and prepare content
    user_messages = [{"role": msg["role"], "content": msg["content"]}
                     for msg in conversation_messages if msg["role"] == "user"]

    # Combine all user messages with the title prompt
    combined_content = "\n".join([msg["content"] for msg in user_messages])
    final_prompt = f"Generate a title for:\n{combined_content}"

    try:
        # Get title agent name from settings
        title_agent_name = app_settings.azure_ai.agent_name_title
        if not title_agent_name:
            logging.warning("Title agent name not configured, using fallback")
            return user_messages[-1]["content"][:50] if user_messages else "New Conversation"

        async with (
            await get_azure_credential_async(client_id=app_settings.base_settings.azure_client_id) as credential,
            AIProjectClient(endpoint=app_settings.azure_ai.agent_endpoint, credential=credential) as project_client,
        ):
            # Create chat client with title agent
            chat_client = AzureAIClient(
                project_client=project_client,
                agent_name=title_agent_name,
                use_latest_version=True,
            )

            # Use ChatAgent to generate title
            async with ChatAgent(
                chat_client=chat_client,
                tool_choice="none",
            ) as chat_agent:
                thread = chat_agent.get_new_thread()
                result = await chat_agent.run(messages=final_prompt, thread=thread)
                title = str(result).strip() if result is not None else "New Conversation"
                track_event_if_configured("TitleGenerated", {"title": title})
                return title

    except Exception as e:
        logging.exception(f"Exception in generate_title: {e}")
        # Fallback to user message or default
        if user_messages:
            return user_messages[-1]["content"][:50]
        return "New Conversation"


async def get_section_content(request_body, request_headers):
    """
    Generate section content using the Section Agent.

    Args:
        request_body: Request body containing sectionTitle and sectionDescription
        request_headers: Request headers

    Returns:
        str: Generated section content
    """
    user_prompt = f"""sectionTitle: {request_body['sectionTitle']}
    sectionDescription: {request_body['sectionDescription']}
    """

    try:
        # Get section agent name from settings
        section_agent_name = app_settings.azure_ai.agent_name_section
        if not section_agent_name:
            logging.error("Section agent name not configured")
            raise ValueError("Section agent name not configured")

        async with (
            await get_azure_credential_async(client_id=app_settings.base_settings.azure_client_id) as credential,
            AIProjectClient(endpoint=app_settings.azure_ai.agent_endpoint, credential=credential) as project_client,
        ):
            # Create chat client with section agent
            chat_client = AzureAIClient(
                project_client=project_client,
                agent_name=section_agent_name,
                use_latest_version=True,
            )

            # Use ChatAgent to generate section content
            async with ChatAgent(
                chat_client=chat_client,
                tool_choice="auto",
                store=True,
            ) as chat_agent:
                result = await chat_agent.run(messages=user_prompt)
                response_text = str(result) if result is not None else ""

                # Remove citation markers from section content
                response_text = re.sub(r'【(\d+:\d+)†source】', '', response_text)

                track_event_if_configured("SectionContentGenerated", {
                    "sectionTitle": request_body["sectionTitle"]
                })

                return response_text

    except Exception as e:
        logging.exception(f"Exception in get_section_content: {e}")
        span = trace.get_current_span()
        if span is not None:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
        raise e


app = create_app()
