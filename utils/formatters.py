"""Response formatters and utilities."""

from typing import Dict, Any, List, Optional
from datetime import datetime

def format_chat_response(orchestrator_result: Dict[str, Any]) -> Dict[str, Any]:
    """Format the orchestrator result for the chat API response."""
    
    return {
        "response": orchestrator_result.get("response", "I'm here to help with your request."),
        "plan": orchestrator_result.get("plan_executed", {}),
        "agents_used": orchestrator_result.get("plan_executed", {}).get("agents_involved", []),
        "tools_used": orchestrator_result.get("tools_used", []),
        "confidence": orchestrator_result.get("confidence", 0.5),
        "thinking_process": orchestrator_result.get("thinking_process", ""),
        "execution_time": orchestrator_result.get("execution_time", 0),
        "timestamp": datetime.now().isoformat()
    }

def format_session_response(session_id: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Format session data for the session API response."""
    
    return {
        "session_id": session_id,
        "conversation_length": len(conversation_history),
        "conversation": conversation_history,
        "last_activity": conversation_history[-1]["timestamp"] if conversation_history else None
    }

def format_agents_response() -> Dict[str, Any]:
    """Format the agents information for the agents API response."""
    
    return {
        "available_agents": {
            "orchestrator": {
                "name": "Orchestrator",
                "description": "Main coordinator that manages all specialist agents",
                "capabilities": ["Multi-agent coordination", "Response synthesis", "Plan execution"]
            },
            "order": {
                "name": "Order Specialist",
                "description": "Handles order tracking, modifications, returns, and warranty issues",
                "capabilities": ["Order lookup", "Tracking information", "Returns processing", "Warranty checks"]
            },
            "tech_support": {
                "name": "Technical Support",
                "description": "Provides troubleshooting and technical assistance",
                "capabilities": ["Hardware troubleshooting", "Software issues", "Setup guidance", "Performance optimization"]
            },
            "product": {
                "name": "Product Expert",
                "description": "Offers product information, comparisons, and recommendations",
                "capabilities": ["Product specifications", "Comparisons", "Recommendations", "Inventory checks"]
            },
            "solutions": {
                "name": "Solutions Specialist", 
                "description": "Handles returns, exchanges, and problem resolution",
                "capabilities": ["Returns processing", "Exchange requests", "Compensation decisions", "Problem resolution"]
            }
        },
        "execution_modes": [
            {
                "mode": "sequential",
                "description": "Agents execute one after another, sharing context"
            },
            {
                "mode": "parallel", 
                "description": "Multiple agents work simultaneously for faster response"
            },
            {
                "mode": "conditional",
                "description": "Agents execute based on dependencies and conditions"
            }
        ]
    }

def format_demo_response() -> Dict[str, Any]:
    """Format the demo scenario response."""
    
    demo_scenario = {
        "scenario": "Customer Technical Support with Order Context",
        "customer_message": "My laptop order #12345 won't turn on, I need help!",
        "expected_flow": [
            {
                "step": 1,
                "agent": "Order Agent",
                "action": "Retrieve order #12345 details and warranty information"
            },
            {
                "step": 2, 
                "agent": "Tech Support Agent",
                "action": "Provide troubleshooting steps for laptop power issues"
            },
            {
                "step": 3,
                "agent": "Solutions Agent", 
                "action": "Offer resolution options (repair, replacement, refund)"
            },
            {
                "step": 4,
                "agent": "Orchestrator",
                "action": "Synthesize all responses into coherent customer support answer"
            }
        ],
        "demonstration_features": [
            "Multi-agent coordination",
            "Context sharing between agents",
            "Tool usage (order lookup, knowledge base, troubleshooting)",
            "Intelligent response synthesis",
            "Real-time execution planning"
        ]
    }
    
    return demo_scenario

def format_error_response(error_message: str, error_type: str = "general_error") -> Dict[str, Any]:
    """Format error responses consistently."""
    
    return {
        "error": True,
        "error_type": error_type,
        "message": error_message,
        "timestamp": datetime.now().isoformat(),
        "suggestion": "Please try again or contact support if the issue persists"
    }

def format_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format success responses consistently."""
    
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data:
        response["data"] = data
    
    return response

def truncate_response(text: str, max_length: int = 2000) -> str:
    """Truncate response text if it's too long."""
    
    if len(text) <= max_length:
        return text
    
    # Try to truncate at a sentence boundary
    truncated = text[:max_length]
    last_sentence_end = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence_end > max_length * 0.7:  # If we can keep at least 70% of the text
        return truncated[:last_sentence_end + 1] + "..."
    else:
        return truncated + "..."

def highlight_key_info(text: str, keywords: List[str]) -> str:
    """Highlight key information in the response text."""
    
    # For terminal output, we can use simple formatting
    highlighted = text
    
    for keyword in keywords:
        if keyword.lower() in text.lower():
            # Simple highlighting - in a real implementation, you might use rich text
            highlighted = highlighted.replace(keyword, f"**{keyword}**")
    
    return highlighted