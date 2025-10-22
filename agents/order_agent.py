"""Order specialist agent for handling order-related queries."""

import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from tools.order_tools import order_tools

logger = logging.getLogger(__name__)

class OrderAgent(BaseAgent):
    """Specialized agent for order management and tracking."""
    
    def __init__(self):
        super().__init__("order")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the order agent."""
        return """
        You are an Order Management Specialist for a customer service team. Your expertise includes:
        
        - Order lookup and status tracking
        - Delivery and shipping information
        - Order modifications and cancellations
        - Return and exchange processes
        - Warranty status and coverage
        - Billing and payment issues
        
        Guidelines:
        - Always verify order information before making changes
        - Provide accurate delivery estimates and tracking information
        - Explain return and warranty policies clearly
        - Offer alternatives when modifications aren't possible
        - Be empathetic about order issues and delays
        - Escalate complex billing issues to appropriate teams
        
        Use the available tools to retrieve accurate order information and provide helpful solutions.
        Keep responses concise but comprehensive, focusing on resolving the customer's specific order concerns.
        """
    
    async def process_request(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process order-related requests."""
        try:
            # Extract order ID from message if present
            order_id = self._extract_order_id(user_message, context)
            tool_results = []
            tools_used = []
            
            if order_id:
                # Get order information
                order_info = await order_tools.get_order_info(order_id)
                if order_info:
                    tool_results.append({
                        "tool": "get_order_info",
                        "result": order_info
                    })
                    tools_used.append("order_lookup")
                    
                    # Check if warranty info is needed
                    if "warranty" in user_message.lower():
                        warranty_info = await order_tools.check_warranty(order_id)
                        tool_results.append({
                            "tool": "check_warranty",
                            "result": warranty_info
                        })
                        tools_used.append("warranty_check")
                    
                    # Check if tracking info is needed
                    if any(word in user_message.lower() for word in ["track", "shipping", "delivery", "where is"]):
                        tracking_info = await order_tools.track_shipment(order_id)
                        tool_results.append({
                            "tool": "track_shipment",
                            "result": tracking_info
                        })
                        tools_used.append("shipment_tracking")
                    
                    # Check if return is requested
                    if any(word in user_message.lower() for word in ["return", "exchange", "refund"]):
                        return_reason = self._extract_return_reason(user_message)
                        return_info = await order_tools.initiate_return(order_id, return_reason)
                        tool_results.append({
                            "tool": "initiate_return",
                            "result": return_info
                        })
                        tools_used.append("return_processing")
            
            # Generate AI response with context and tool results
            agent_response = await self.generate_response(
                user_message, 
                {**context, "tool_results": tool_results},
                tools_used
            )
            
            return self.format_final_response(agent_response, tool_results)
            
        except Exception as e:
            logger.error(f"Error in OrderAgent.process_request: {e}")
            return {
                "response": "I apologize, but I'm having trouble accessing order information right now. Please provide your order number and I'll help you as soon as possible.",
                "agent_used": self.agent_type,
                "tools_used": [],
                "tool_results": [],
                "confidence": 0.3,
                "thinking_process": f"Error occurred while processing order request: {str(e)}"
            }
    
    def _extract_order_id(self, message: str, context: Dict[str, Any]) -> str:
        """Extract order ID from message or context."""
        import re
        
        # Try to find order number in message
        order_pattern = r'order\s*#?(\d+)'
        match = re.search(order_pattern, message.lower())
        if match:
            return match.group(1)
        
        # Check context for previously discussed orders
        if context.get("orders_discussed"):
            return context["orders_discussed"][-1]  # Return most recent
        
        return None
    
    def _extract_return_reason(self, message: str) -> str:
        """Extract return reason from message."""
        message_lower = message.lower()
        
        # Map keywords to return reasons
        reason_map = {
            "defective": "defective",
            "broken": "defective", 
            "damaged": "damaged_shipping",
            "wrong": "wrong_item",
            "not working": "defective",
            "doesn't work": "defective",
            "won't turn on": "defective",
            "performance": "performance_issue",
            "slow": "performance_issue",
            "changed mind": "customer_preference",
            "don't need": "customer_preference",
            "size": "size_issue"
        }
        
        for keyword, reason in reason_map.items():
            if keyword in message_lower:
                return reason
        
        return "other"  # Default reason