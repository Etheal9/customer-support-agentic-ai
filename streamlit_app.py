"""
Streamlit Demo Application for Multi-Agent Customer Care System
A beautiful, interactive chat interface showcasing coordinated AI agents.
"""

import streamlit as st
import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import orchestrator
from memory.session_memory import memory
from config import REQUEST_TIMEOUT

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Customer Care Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        margin: 2px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        color: #1a1a1a !important;
    }
    
    .agent-order { background-color: #4CAF50; }
    .agent-tech { background-color: #2196F3; }
    .agent-product { background-color: #FF9800; }
    .agent-solutions { background-color: #9C27B0; }
    .agent-orchestrator { background-color: #607D8B; }
    
    .execution-step {
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
        border-radius: 5px;
        color: #2c2c2c !important;
    }
    
    .memory-item {
        background-color: #e8f4fd;
        padding: 8px;
        margin: 4px 0;
        border-radius: 5px;
        font-size: 14px;
        color: #2c2c2c !important;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
        color: #000000 !important;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        margin-right: 20%;
        color: #000000 !important;
    }
    
    .agent-activity {
        background-color: #fff3e0;
        border: 1px solid #ffcc02;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #2c2c2c !important;
    }
    
    .status-executing { 
        background-color: #ffc107; 
        animation: pulse 1.5s infinite;
    }
    
    .status-completed { background-color: #28a745; }
    .status-pending { background-color: #6c757d; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Only apply dark text to specific light-colored elements */
    .execution-step, .memory-item, .agent-activity {
        /* Dark text already applied above */
    }
    
    /* Keep the chat messages with proper contrast */
    .user-message, .assistant-message {
        /* Black text already applied above for light backgrounds */
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"streamlit-{int(time.time())}"
    
    if "agent_activity" not in st.session_state:
        st.session_state.agent_activity = []
    
    if "memory_context" not in st.session_state:
        st.session_state.memory_context = {}
    
    if "execution_plan" not in st.session_state:
        st.session_state.execution_plan = None

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Multi-Agent Customer Care System</h1>
        <p>Watch AI agents collaborate to solve customer problems</p>
    </div>
    """, unsafe_allow_html=True)

def get_agent_badge_html(agent_type: str, status: str = "active") -> str:
    """Generate HTML for agent badge."""
    status_class = f"status-{status}" if status != "active" else ""
    return f'<span class="agent-badge agent-{agent_type} {status_class}">🤖 {agent_type.title()}</span>'

def display_agent_activity():
    """Display current agent activity in sidebar."""
    st.sidebar.markdown("### 🔄 Agent Activity")
    
    if st.session_state.agent_activity:
        for activity in st.session_state.agent_activity[-5:]:  # Show last 5 activities
            agent = activity.get("agent", "unknown")
            status = activity.get("status", "active")
            action = activity.get("action", "Processing...")
            
            badge_html = get_agent_badge_html(agent, status)
            st.sidebar.markdown(f"{badge_html}", unsafe_allow_html=True)
            st.sidebar.caption(f"_{action}_")
            st.sidebar.markdown("---")
    else:
        st.sidebar.info("No agent activity yet. Send a message to see agents in action!")

def display_memory_context():
    """Display current memory context in sidebar."""
    st.sidebar.markdown("### 🧠 Memory Context")
    
    if st.session_state.memory_context:
        context = st.session_state.memory_context
        
        # Orders discussed
        if context.get("orders_discussed"):
            st.sidebar.markdown("**Orders Discussed:**")
            for order_id in context["orders_discussed"][-3:]:
                st.sidebar.markdown(f'<div class="memory-item">📦 Order #{order_id}</div>', 
                                  unsafe_allow_html=True)
        
        # Products discussed
        if context.get("products_discussed"):
            st.sidebar.markdown("**Products Mentioned:**")
            for product in context["products_discussed"][-3:]:
                st.sidebar.markdown(f'<div class="memory-item">💻 {product}</div>', 
                                  unsafe_allow_html=True)
        
        # Issues mentioned
        if context.get("issues_mentioned"):
            st.sidebar.markdown("**Issues Identified:**")
            for issue in context["issues_mentioned"][-3:]:
                st.sidebar.markdown(f'<div class="memory-item">⚠️ {issue}</div>', 
                                  unsafe_allow_html=True)
        
        # Conversation length
        conv_length = context.get("conversation_length", 0)
        st.sidebar.metric("Conversation Length", f"{conv_length} messages")
        
    else:
        st.sidebar.info("Memory context will appear as you chat")

def display_execution_plan():
    """Display the current execution plan."""
    if st.session_state.execution_plan:
        plan = st.session_state.execution_plan
        
        st.markdown("### 📋 Execution Plan")
        st.markdown(f"**Plan ID:** `{plan.get('plan_id', 'N/A')}`")
        st.markdown(f"**Execution Mode:** `{plan.get('execution_mode', 'unknown')}`")
        
        if plan.get("steps"):
            st.markdown("**Agent Coordination Steps:**")
            for i, step in enumerate(plan["steps"], 1):
                agent = step.get("agent", "unknown")
                status = step.get("status", "pending")
                task = step.get("task", "Processing...")
                
                badge_html = get_agent_badge_html(agent, status)
                st.markdown(f"""
                <div class="execution-step">
                    <strong>Step {i}:</strong> {badge_html}<br>
                    <em>{task}</em>
                </div>
                """, unsafe_allow_html=True)

def process_message_simple(user_message: str) -> Dict[str, Any]:
    """Process user message through individual agents - simplified approach."""
    
    # Clear previous agent activity
    st.session_state.agent_activity = []
    
    # Import agents
    from agents.tech_support_agent import TechSupportAgent
    from agents.order_agent import OrderAgent
    from agents.product_agent import ProductAgent
    from agents.solutions_agent import SolutionsAgent
    
    # Simple context
    context = {"recent_conversation": []}
    
    # Determine which agent to use based on keywords
    user_lower = user_message.lower()
    
    try:
        if "order" in user_lower or any(c.isdigit() for c in user_message):
            agent = OrderAgent()
            agent_name = "Order"
        elif any(word in user_lower for word in ["won't turn on", "broken", "issue", "problem", "technical", "fix"]):
            agent = TechSupportAgent()
            agent_name = "Tech Support"
        elif any(word in user_lower for word in ["return", "refund", "exchange", "solution"]):
            agent = SolutionsAgent()
            agent_name = "Solutions"
        else:
            agent = ProductAgent()
            agent_name = "Product"
        
        # Process with the selected agent
        result = asyncio.run(agent.process_request(user_message, context))
        
        # Add agent activity
        st.session_state.agent_activity.append({
            "agent": agent_name.lower().replace(" ", "_"),
            "status": "completed",
            "action": f"Provided {agent_name.lower()} assistance"
        })
        
        return {
            "response": result.get("response", "I'm here to help with your request!"),
            "agent_used": agent_name,
            "confidence": result.get("confidence", 0.8)
        }
        
    except Exception as e:
        return {
            "response": f"I understand you need help! Let me assist you with that. Could you provide more details about your specific issue?",
            "agent_used": "Fallback",
            "confidence": 0.6,
            "error": str(e)
        }

def display_chat_interface():
    """Display the main chat interface."""
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Assistant message with agent info
                agent_info = ""
                if message.get("agents_used"):
                    agent_badges = " ".join([
                        get_agent_badge_html(agent) 
                        for agent in message["agents_used"]
                    ])
                    agent_info = f"<br><small>Agents used: {agent_badges}</small>"
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Assistant:</strong> {message["content"]}{agent_info}
                </div>
                """, unsafe_allow_html=True)
                
                # Show execution details in expander
                if message.get("plan_executed"):
                    with st.expander("🔍 View Agent Coordination Details"):
                        plan = message["plan_executed"]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Agents Used", len(plan.get("agents_involved", [])))
                        with col2:
                            st.metric("Tools Used", len(plan.get("tools_used", [])))
                        with col3:
                            st.metric("Execution Time", f"{message.get('execution_time', 0):.1f}s")
                        
                        if plan.get("steps"):
                            st.markdown("**Execution Steps:**")
                            for step in plan["steps"]:
                                status_emoji = "✅" if step.get("status") == "completed" else "⏳"
                                st.write(f"{status_emoji} **{step.get('agent', 'Unknown')}**: {step.get('task', 'Task')}")

def display_example_questions():
    """Display example questions for easy testing."""
    st.markdown("### 💡 Try These Demo Questions")
    
    examples = [
        {
            "category": "🛒 Order Support",
            "questions": [
                "My laptop order #12345 won't turn on, I need help!",
                "I want to track my order #12346",
                "How do I return order #12345?",
                "Is my order #12345 still under warranty?"
            ]
        },
        {
            "category": "💻 Product Questions", 
            "questions": [
                "Compare TechBook Pro 15 vs TechBook Air 13",
                "What laptops do you have under $1000?",
                "I need a laptop for gaming, what do you recommend?",
                "What are the specs of the TechBook Gaming 17?"
            ]
        },
        {
            "category": "🔧 Technical Support",
            "questions": [
                "My laptop is overheating, what should I do?",
                "The WiFi on my laptop isn't working",
                "My laptop is running very slowly",
                "The screen on my laptop is flickering"
            ]
        },
        {
            "category": "🔄 Follow-up Questions",
            "questions": [
                "What other options do I have?",
                "Can you explain that in more detail?",
                "What would you recommend instead?",
                "How long will this take?"
            ]
        }
    ]
    
    for category in examples:
        with st.expander(category["category"]):
            for question in category["questions"]:
                if st.button(question, key=f"btn_{hash(question)}"):
                    st.session_state.selected_question = question
                    st.rerun()

def main():
    """Main Streamlit application."""
    
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Create layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat with Multi-Agent System")
        
        # Display chat interface
        display_chat_interface()
        
        # Handle selected question from examples
        if hasattr(st.session_state, 'selected_question'):
            user_message = st.session_state.selected_question
            delattr(st.session_state, 'selected_question')
        else:
            # Chat input
            user_message = st.chat_input("Ask me anything about orders, products, or technical support...")
        
        if user_message:
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show processing indicator
            with st.spinner("🤖 Agents are working on your request..."):
                # Process message with simplified approach
                try:
                    start_time = time.time()
                    result = process_message_simple(user_message)
                    processing_time = time.time() - start_time
                    
                    # Add assistant response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.get("response", "I apologize, but I encountered an issue processing your request."),
                        "agents_used": [result.get("agent_used", "Unknown")],
                        "execution_time": processing_time,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if result.get("error"):
                        st.warning(f"Note: {result['error']}")
                    
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I apologize for the technical issue. Let me help you directly - what specific problem are you facing? I can assist with orders, technical support, product recommendations, or returns.",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Rerun to update the display
            st.rerun()
    
    with col2:
        # Right sidebar content
        st.markdown("### 🎯 System Status")
        
        # Session info
        st.info(f"**Session:** `{st.session_state.session_id}`")
        
        # Display agent activity
        display_agent_activity()
        
        # Display memory context  
        display_memory_context()
        
        # Reset conversation button
        if st.button("🔄 Reset Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.agent_activity = []
            st.session_state.memory_context = {}
            st.session_state.execution_plan = None
            memory.clear_session(st.session_state.session_id)
            st.success("Conversation reset!")
            st.rerun()
    
    # Display example questions at the bottom
    st.markdown("---")
    display_example_questions()
    
    # Display execution plan if available
    if st.session_state.execution_plan:
        with st.expander("📋 Latest Execution Plan", expanded=False):
            display_execution_plan()

if __name__ == "__main__":
    main()