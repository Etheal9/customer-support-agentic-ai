"""Main FastAPI application for the multi-agent customer care system."""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agents.orchestrator import orchestrator
from memory.session_memory import memory
from utils.logging_config import setup_logging
from utils.formatters import (
    format_chat_response, 
    format_session_response, 
    format_agents_response,
    format_demo_response,
    format_error_response,
    format_success_response
)
from config import REQUEST_TIMEOUT

# Set up logging
setup_logging()
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("🚀 Multi-Agent Customer Care System starting up...")
    
    # Startup
    logger.info("✅ All agents initialized and ready")
    logger.info("✅ Memory system active")
    logger.info("✅ API endpoints configured")
    
    yield
    
    # Shutdown
    logger.info("🔄 Multi-Agent Customer Care System shutting down...")
    memory.clear_all_sessions()
    logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Customer Care System",
    description="A demonstration of coordinated AI agents providing comprehensive customer support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., description="Customer message")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")

class ChatResponse(BaseModel):
    response: str
    plan: dict
    agents_used: list
    tools_used: list
    confidence: float
    thinking_process: str
    execution_time: float
    timestamp: str

# API Endpoints

@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint."""
    return {
        "status": "active",
        "system": "Multi-Agent Customer Care System",
        "version": "1.0.0",
        "agents_available": len(orchestrator.agents) + 1,  # +1 for orchestrator
        "memory_sessions": len(memory.get_all_session_ids())
    }

@app.post("/chat", response_model=ChatResponse, summary="Process Customer Message")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Process a customer message using the multi-agent system.
    
    The orchestrator will:
    1. Analyze the request and create an execution plan
    2. Coordinate appropriate specialist agents
    3. Synthesize responses into a coherent answer
    4. Update conversation memory
    """
    try:
        logger.info(f"📨 New chat request: '{request.message[:50]}...' (Session: {request.session_id})")
        
        # Get or create session
        session_id, session = memory.get_or_create_session(request.session_id)
        logger.info(f"💬 Using session: {session_id}")
        
        # Process request with timeout
        try:
            result = await asyncio.wait_for(
                orchestrator.process_request(request.message, session_id),
                timeout=REQUEST_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"⏰ Request timeout after {REQUEST_TIMEOUT}s")
            raise HTTPException(
                status_code=504,
                detail=f"Request timeout after {REQUEST_TIMEOUT} seconds. Please try a simpler request."
            )
        
        # Format response
        formatted_response = format_chat_response(result)
        formatted_response["session_id"] = session_id
        
        logger.info(f"✅ Chat response generated successfully (confidence: {result.get('confidence', 0):.2f})")
        
        return formatted_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/session/{session_id}", summary="Get Session History")
async def get_session(session_id: str):
    """
    Retrieve conversation history for a specific session.
    """
    try:
        history = memory.get_conversation_history(session_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or expired"
            )
        
        return format_session_response(session_id, history)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )

@app.post("/reset", summary="Reset All Sessions")
async def reset_sessions():
    """
    Clear all conversation sessions for demo reset.
    """
    try:
        session_count = len(memory.get_all_session_ids())
        memory.clear_all_sessions()
        
        logger.info(f"🔄 Reset {session_count} sessions")
        
        return format_success_response(
            f"Successfully reset {session_count} sessions",
            {"sessions_cleared": session_count}
        )
        
    except Exception as e:
        logger.error(f"Error resetting sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting sessions: {str(e)}"
        )

@app.get("/agents", summary="List Available Agents")
async def get_agents():
    """
    Get information about all available agents and their capabilities.
    """
    try:
        return format_agents_response()
        
    except Exception as e:
        logger.error(f"Error retrieving agents info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agents info: {str(e)}"
        )

@app.get("/demo", summary="Run Demo Scenario")
async def run_demo():
    """
    Run a pre-scripted demo scenario showing multi-agent collaboration.
    """
    try:
        logger.info("🎭 Running demo scenario...")
        
        # Demo scenario: Customer with laptop issue
        demo_message = "My laptop order #12345 won't turn on, I need help!"
        
        # Create demo session
        demo_session_id, _ = memory.get_or_create_session("demo-session")
        
        # Process the demo request
        result = await orchestrator.process_request(demo_message, demo_session_id)
        
        # Format demo response with scenario info
        demo_info = format_demo_response()
        demo_response = format_chat_response(result)
        
        logger.info("✅ Demo scenario completed successfully")
        
        return {
            "demo_info": demo_info,
            "execution_result": demo_response,
            "session_id": demo_session_id
        }
        
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running demo: {str(e)}"
        )

@app.get("/sessions", summary="List Active Sessions") 
async def list_sessions():
    """
    List all active session IDs.
    """
    try:
        session_ids = memory.get_all_session_ids()
        
        return {
            "active_sessions": session_ids,
            "session_count": len(session_ids),
            "timestamp": format_chat_response({})["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=format_error_response(
            "Endpoint not found",
            "not_found"
        )
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            "Internal server error",
            "internal_error"
        )
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🎯 Starting Multi-Agent Customer Care System Demo")
    logger.info("📋 Available endpoints:")
    logger.info("   POST /chat - Process customer messages") 
    logger.info("   GET  /session/{id} - Get conversation history")
    logger.info("   GET  /agents - List available agents")
    logger.info("   GET  /demo - Run demo scenario")
    logger.info("   POST /reset - Reset all sessions")
    logger.info("")
    logger.info("🌐 API will be available at: http://localhost:8000")
    logger.info("📖 Interactive docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )