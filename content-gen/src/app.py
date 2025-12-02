"""
Content Generation Solution Accelerator - Main Application Entry Point.

This is the main Quart application that provides the REST API for the
Intelligent Content Generation Accelerator.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

from quart import Quart, request, jsonify, Response
from quart_cors import cors

from backend.settings import app_settings
from backend.models import CreativeBrief, Product
from backend.orchestrator import get_orchestrator
from backend.services.cosmos_service import get_cosmos_service
from backend.services.blob_service import get_blob_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")


# ==================== Health Check ====================

@app.route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    })


# ==================== Chat Endpoints ====================

@app.route("/api/chat", methods=["POST"])
async def chat():
    """
    Process a chat message through the agent orchestration.
    
    Request body:
    {
        "message": "User's message",
        "conversation_id": "optional-uuid",
        "user_id": "user identifier"
    }
    
    Returns streaming response with agent responses.
    """
    data = await request.get_json()
    
    message = data.get("message", "")
    conversation_id = data.get("conversation_id") or str(uuid.uuid4())
    user_id = data.get("user_id", "anonymous")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    orchestrator = get_orchestrator()
    
    # Try to save to CosmosDB but don't fail if it's unavailable
    try:
        cosmos_service = await get_cosmos_service()
        await cosmos_service.add_message_to_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message={
                "role": "user",
                "content": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.warning(f"Failed to save message to CosmosDB: {e}")
    
    async def generate():
        """Stream responses from the orchestrator."""
        try:
            async for response in orchestrator.process_message(
                message=message,
                conversation_id=conversation_id
            ):
                yield f"data: {json.dumps(response)}\n\n"
                
                # Save assistant responses when final OR when requiring user input
                if response.get("is_final") or response.get("requires_user_input"):
                    if response.get("content"):
                        try:
                            cosmos_service = await get_cosmos_service()
                            await cosmos_service.add_message_to_conversation(
                                conversation_id=conversation_id,
                                user_id=user_id,
                                message={
                                    "role": "assistant",
                                    "content": response.get("content", ""),
                                    "agent": response.get("agent", ""),
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            )
                        except Exception as e:
                            logger.warning(f"Failed to save response to CosmosDB: {e}")
        except Exception as e:
            logger.exception(f"Error in orchestrator: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'is_final': True})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# ==================== Creative Brief Endpoints ====================

@app.route("/api/brief/parse", methods=["POST"])
async def parse_brief():
    """
    Parse a free-text creative brief into structured format.
    
    Request body:
    {
        "brief_text": "Free-form creative brief text",
        "conversation_id": "optional-uuid",
        "user_id": "user identifier"
    }
    
    Returns:
        Structured CreativeBrief JSON for user confirmation.
    """
    data = await request.get_json()
    brief_text = data.get("brief_text", "")
    conversation_id = data.get("conversation_id") or str(uuid.uuid4())
    user_id = data.get("user_id", "anonymous")
    
    if not brief_text:
        return jsonify({"error": "Brief text is required"}), 400
    
    # Save the user's brief text as a message to CosmosDB
    try:
        cosmos_service = await get_cosmos_service()
        await cosmos_service.add_message_to_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message={
                "role": "user",
                "content": brief_text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.warning(f"Failed to save brief message to CosmosDB: {e}")
    
    orchestrator = get_orchestrator()
    parsed_brief = await orchestrator.parse_brief(brief_text)
    
    # Save the assistant's parsing response
    try:
        cosmos_service = await get_cosmos_service()
        await cosmos_service.add_message_to_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message={
                "role": "assistant",
                "content": "I've parsed your creative brief. Please review and confirm the details before we proceed.",
                "agent": "PlanningAgent",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.warning(f"Failed to save parsing response to CosmosDB: {e}")
    
    return jsonify({
        "brief": parsed_brief.model_dump(),
        "requires_confirmation": True,
        "conversation_id": conversation_id,
        "message": "Please review and confirm the parsed creative brief"
    })


@app.route("/api/brief/confirm", methods=["POST"])
async def confirm_brief():
    """
    Confirm or modify a parsed creative brief.
    
    Request body:
    {
        "brief": { ... CreativeBrief fields ... },
        "conversation_id": "optional-uuid",
        "user_id": "user identifier"
    }
    
    Returns:
        Confirmation status and next steps.
    """
    data = await request.get_json()
    brief_data = data.get("brief", {})
    conversation_id = data.get("conversation_id") or str(uuid.uuid4())
    user_id = data.get("user_id", "anonymous")
    
    try:
        brief = CreativeBrief(**brief_data)
    except Exception as e:
        return jsonify({"error": f"Invalid brief format: {str(e)}"}), 400
    
    # Try to save the confirmed brief to CosmosDB, preserving existing messages
    try:
        cosmos_service = await get_cosmos_service()
        
        # Get existing conversation to preserve messages
        existing = await cosmos_service.get_conversation(conversation_id, user_id)
        existing_messages = existing.get("messages", []) if existing else []
        
        # Add confirmation message
        existing_messages.append({
            "role": "assistant",
            "content": "Great! Your creative brief has been confirmed. Now you can select products to feature and generate content.",
            "agent": "TriageAgent",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await cosmos_service.save_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            messages=existing_messages,
            brief=brief,
            metadata={"status": "brief_confirmed"}
        )
    except Exception as e:
        logger.warning(f"Failed to save brief to CosmosDB: {e}")
    
    return jsonify({
        "status": "confirmed",
        "conversation_id": conversation_id,
        "brief": brief.model_dump(),
        "message": "Brief confirmed. Ready for content generation."
    })


# ==================== Content Generation Endpoints ====================

@app.route("/api/generate", methods=["POST"])
async def generate_content():
    """
    Generate content from a confirmed creative brief.
    
    Request body:
    {
        "brief": { ... CreativeBrief fields ... },
        "products": [ ... Product list (optional) ... ],
        "generate_images": true/false,
        "conversation_id": "uuid"
    }
    
    Returns streaming response with generated content.
    """
    data = await request.get_json()
    
    brief_data = data.get("brief", {})
    products_data = data.get("products", [])
    generate_images = data.get("generate_images", True)
    conversation_id = data.get("conversation_id") or str(uuid.uuid4())
    user_id = data.get("user_id", "anonymous")
    
    try:
        brief = CreativeBrief(**brief_data)
    except Exception as e:
        return jsonify({"error": f"Invalid brief format: {str(e)}"}), 400
    
    # Save user request for content generation
    try:
        cosmos_service = await get_cosmos_service()
        product_names = [p.get("product_name", "product") for p in products_data[:3]]
        await cosmos_service.add_message_to_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message={
                "role": "user",
                "content": f"Generate content for: {', '.join(product_names) if product_names else 'the campaign'}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.warning(f"Failed to save generation request to CosmosDB: {e}")
    
    orchestrator = get_orchestrator()
    
    async def generate():
        """Stream content generation responses."""
        try:
            response = await orchestrator.generate_content(
                brief=brief,
                products=products_data,
                generate_images=generate_images
            )
            
            # Try to save generated images to blob storage
            try:
                blob_service = await get_blob_service()
                if response.get("image_base64"):
                    image_url = await blob_service.save_generated_image(
                        conversation_id=conversation_id,
                        image_base64=response["image_base64"]
                    )
                    response["image_url"] = image_url
            except Exception as e:
                logger.warning(f"Failed to save image to blob storage: {e}")
            
            # Save generated content to conversation
            try:
                cosmos_service = await get_cosmos_service()
                text_content = response.get("text_content", {})
                headline = text_content.get("headline", "") if isinstance(text_content, dict) else ""
                await cosmos_service.add_message_to_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message={
                        "role": "assistant",
                        "content": f"Content generated successfully! {f'Headline: "{headline}"' if headline else ''}",
                        "agent": "ContentAgent",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to save generated content to CosmosDB: {e}")
            
            # Format response to match what frontend expects
            yield f"data: {json.dumps({'type': 'agent_response', 'content': json.dumps(response), 'is_final': True})}\n\n"
        except Exception as e:
            logger.exception(f"Error generating content: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'is_final': True})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# ==================== Product Endpoints ====================

@app.route("/api/products", methods=["GET"])
async def list_products():
    """
    List all products.
    
    Query params:
        category: Filter by category
        sub_category: Filter by sub-category
        search: Search term
        limit: Max number of results (default 20)
    """
    category = request.args.get("category")
    sub_category = request.args.get("sub_category")
    search = request.args.get("search")
    limit = int(request.args.get("limit", 20))
    
    cosmos_service = await get_cosmos_service()
    
    if search:
        products = await cosmos_service.search_products(search, limit)
    elif category:
        products = await cosmos_service.get_products_by_category(
            category, sub_category, limit
        )
    else:
        products = await cosmos_service.get_all_products(limit)
    
    return jsonify({
        "products": [p.model_dump() for p in products],
        "count": len(products)
    })


@app.route("/api/products/<sku>", methods=["GET"])
async def get_product(sku: str):
    """Get a product by SKU."""
    cosmos_service = await get_cosmos_service()
    product = await cosmos_service.get_product_by_sku(sku)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(product.model_dump())


@app.route("/api/products", methods=["POST"])
async def create_product():
    """
    Create or update a product.
    
    Request body:
    {
        "product_name": "...",
        "category": "...",
        "sub_category": "...",
        "marketing_description": "...",
        "detailed_spec_description": "...",
        "sku": "...",
        "model": "..."
    }
    """
    data = await request.get_json()
    
    try:
        product = Product(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid product format: {str(e)}"}), 400
    
    cosmos_service = await get_cosmos_service()
    saved_product = await cosmos_service.upsert_product(product)
    
    return jsonify(saved_product.model_dump()), 201


@app.route("/api/products/<sku>/image", methods=["POST"])
async def upload_product_image(sku: str):
    """
    Upload an image for a product.
    
    The image will be stored and a description will be auto-generated
    using GPT-5 Vision.
    
    Request: multipart/form-data with 'image' file
    """
    cosmos_service = await get_cosmos_service()
    product = await cosmos_service.get_product_by_sku(sku)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    files = await request.files
    if "image" not in files:
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = files["image"]
    image_data = image_file.read()
    content_type = image_file.content_type or "image/jpeg"
    
    blob_service = await get_blob_service()
    image_url, description = await blob_service.upload_product_image(
        sku=sku,
        image_data=image_data,
        content_type=content_type
    )
    
    # Update product with image info
    product.image_url = image_url
    product.image_description = description
    await cosmos_service.upsert_product(product)
    
    return jsonify({
        "image_url": image_url,
        "image_description": description,
        "message": "Image uploaded and description generated"
    })


# ==================== Conversation Endpoints ====================

@app.route("/api/conversations", methods=["GET"])
async def list_conversations():
    """
    List conversations for a user.
    
    Query params:
        user_id: User identifier (required)
        limit: Max number of results (default 20)
    """
    user_id = request.args.get("user_id")
    limit = int(request.args.get("limit", 20))
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    cosmos_service = await get_cosmos_service()
    conversations = await cosmos_service.get_user_conversations(user_id, limit)
    
    return jsonify({
        "conversations": conversations,
        "count": len(conversations)
    })


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation.
    
    Query params:
        user_id: User identifier (required)
    """
    user_id = request.args.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    cosmos_service = await get_cosmos_service()
    conversation = await cosmos_service.get_conversation(conversation_id, user_id)
    
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404
    
    return jsonify(conversation)


@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
async def delete_conversation(conversation_id: str):
    """
    Delete a specific conversation.
    
    Query params:
        user_id: User identifier (required)
    """
    user_id = request.args.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        cosmos_service = await get_cosmos_service()
        await cosmos_service.delete_conversation(conversation_id, user_id)
        return jsonify({"success": True, "message": "Conversation deleted"})
    except Exception as e:
        logger.warning(f"Failed to delete conversation: {e}")
        return jsonify({"error": "Failed to delete conversation"}), 500


# ==================== Brand Guidelines Endpoints ====================

@app.route("/api/brand-guidelines", methods=["GET"])
async def get_brand_guidelines():
    """Get current brand guidelines configuration."""
    return jsonify({
        "tone": app_settings.brand_guidelines.tone,
        "voice": app_settings.brand_guidelines.voice,
        "primary_color": app_settings.brand_guidelines.primary_color,
        "secondary_color": app_settings.brand_guidelines.secondary_color,
        "prohibited_words": app_settings.brand_guidelines.prohibited_words,
        "required_disclosures": app_settings.brand_guidelines.required_disclosures,
        "max_headline_length": app_settings.brand_guidelines.max_headline_length,
        "max_body_length": app_settings.brand_guidelines.max_body_length,
        "require_cta": app_settings.brand_guidelines.require_cta
    })


# ==================== UI Configuration ====================

@app.route("/api/config", methods=["GET"])
async def get_ui_config():
    """Get UI configuration."""
    return jsonify({
        "app_name": app_settings.ui.app_name,
        "show_brand_guidelines": True,
        "enable_image_generation": True,
        "enable_compliance_check": True,
        "max_file_size_mb": 10
    })


# ==================== Application Lifecycle ====================

@app.before_serving
async def startup():
    """Initialize services on application startup."""
    logger.info("Starting Content Generation Solution Accelerator...")
    
    # Initialize orchestrator
    orchestrator = get_orchestrator()
    logger.info("Orchestrator initialized with Microsoft Agent Framework")
    
    # Try to initialize services - they may fail if CosmosDB/Blob storage is not accessible
    try:
        await get_cosmos_service()
        logger.info("CosmosDB service initialized")
    except Exception as e:
        logger.warning(f"CosmosDB service initialization failed (may be firewall): {e}")
    
    try:
        await get_blob_service()
        logger.info("Blob storage service initialized")
    except Exception as e:
        logger.warning(f"Blob storage service initialization failed: {e}")
    
    logger.info("Application startup complete")


@app.after_serving
async def shutdown():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Content Generation Solution Accelerator...")
    
    cosmos_service = await get_cosmos_service()
    await cosmos_service.close()
    
    blob_service = await get_blob_service()
    await blob_service.close()
    
    logger.info("Application shutdown complete")


# ==================== Error Handlers ====================

@app.errorhandler(404)
async def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
async def server_error(error):
    """Handle 500 errors."""
    logger.exception(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
