"""Technical support specialist agent for troubleshooting and technical issues."""

import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from tools.knowledge_tools import knowledge_tools
from tools.search_tools import search_tools

logger = logging.getLogger(__name__)

class TechSupportAgent(BaseAgent):
    """Specialized agent for technical support and troubleshooting."""
    
    def __init__(self):
        super().__init__("tech_support")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the tech support agent."""
        return """
        You are a Technical Support Specialist for a customer service team. Your expertise includes:
        
        - Hardware troubleshooting and diagnostics
        - Software issues and configuration problems
        - Device setup and installation guidance
        - Performance optimization
        - Driver and firmware updates
        - Network and connectivity issues
        
        Guidelines:
        - Start with basic troubleshooting steps before advanced solutions
        - Explain technical concepts in simple, customer-friendly language
        - Provide step-by-step instructions that are easy to follow
        - Ask clarifying questions to narrow down the problem
        - Know when to escalate to specialized technical teams
        - Always prioritize customer safety (avoid risky procedures)
        
        Use the knowledge base to provide proven troubleshooting steps and search for current solutions when needed.
        Structure your responses with clear steps and explanations for why each step helps.
        """
    
    async def process_request(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical support requests."""
        try:
            tool_results = []
            tools_used = []
            
            # Identify the technical issue
            issue_type = self._identify_issue_type(user_message)
            device_type = self._identify_device_type(user_message, context)
            
            # Search knowledge base for troubleshooting steps
            if issue_type:
                troubleshooting_steps = await knowledge_tools.search_knowledge(issue_type)
                tool_results.append({
                    "tool": "search_knowledge",
                    "result": troubleshooting_steps
                })
                tools_used.append("knowledge_base_search")
                
                # Get comprehensive troubleshooting guide
                if device_type:
                    guide = await knowledge_tools.get_troubleshooting_guide(device_type, issue_type)
                    tool_results.append({
                        "tool": "get_troubleshooting_guide",
                        "result": guide
                    })
                    tools_used.append("troubleshooting_guide")
            
            # Search web for additional help if issue is complex
            if self._is_complex_issue(user_message):
                search_query = f"{device_type} {issue_type} troubleshooting"
                web_results = await search_tools.search_web(search_query)
                tool_results.append({
                    "tool": "search_web",
                    "result": web_results
                })
                tools_used.append("web_search")
            
            # Generate AI response with context and tool results
            agent_response = await self.generate_response(
                user_message,
                {**context, "tool_results": tool_results, "issue_type": issue_type, "device_type": device_type},
                tools_used
            )
            
            return self.format_final_response(agent_response, tool_results)
            
        except Exception as e:
            logger.error(f"Error in TechSupportAgent.process_request: {e}")
            return {
                "response": "I understand you're experiencing a technical issue. Let me help you troubleshoot this step by step. Could you please describe the specific problem you're encountering?",
                "agent_used": self.agent_type,
                "tools_used": [],
                "tool_results": [],
                "confidence": 0.4,
                "thinking_process": f"Error occurred while processing technical support request: {str(e)}"
            }
    
    def _identify_issue_type(self, message: str) -> str:
        """Identify the type of technical issue from the message."""
        message_lower = message.lower()
        
        issue_keywords = {
            "won't turn on": "laptop_wont_turn_on",
            "not turning on": "laptop_wont_turn_on",
            "power": "laptop_wont_turn_on",
            "battery": "laptop_wont_turn_on",
            "overheating": "laptop_overheating",
            "hot": "laptop_overheating",
            "heating": "laptop_overheating",
            "slow": "slow_performance",
            "performance": "slow_performance",
            "lag": "slow_performance",
            "freeze": "slow_performance",
            "wifi": "wifi_issues",
            "internet": "wifi_issues",
            "network": "wifi_issues",
            "connection": "wifi_issues",
            "screen": "screen_issues",
            "display": "screen_issues",
            "monitor": "screen_issues"
        }
        
        for keyword, issue_type in issue_keywords.items():
            if keyword in message_lower:
                return issue_type
        
        return "general_troubleshooting"
    
    def _identify_device_type(self, message: str, context: Dict[str, Any]) -> str:
        """Identify the device type from message or context."""
        message_lower = message.lower()
        
        # Check for specific device mentions
        if "techbook" in message_lower:
            return "techbook"
        elif any(word in message_lower for word in ["laptop", "computer", "notebook"]):
            return "laptop"
        
        # Check context for product discussions
        if context.get("products_discussed"):
            for product in context["products_discussed"]:
                if "techbook" in product.lower():
                    return "techbook"
        
        return "laptop"  # Default assumption
    
    def _is_complex_issue(self, message: str) -> bool:
        """Determine if the issue is complex and needs web search."""
        complex_keywords = [
            "blue screen", "bsod", "kernel", "driver", "firmware", 
            "boot", "startup", "crash", "error code", "specific error"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in complex_keywords)