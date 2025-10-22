"""Solutions specialist agent for returns, exchanges, and problem resolution."""

import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from tools.knowledge_tools import knowledge_tools
from tools.order_tools import order_tools

logger = logging.getLogger(__name__)

class SolutionsAgent(BaseAgent):
    """Specialized agent for customer solutions and problem resolution."""
    
    def __init__(self):
        super().__init__("solutions")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the solutions agent."""
        return """
        You are a Solutions Specialist for a customer service team. Your expertise includes:
        
        - Returns and exchange processing
        - Refund and compensation decisions
        - Problem resolution and escalation
        - Customer satisfaction recovery
        - Policy interpretation and exceptions
        - Alternative solutions and compromises
        
        Guidelines:
        - Always prioritize customer satisfaction while following company policies
        - Look for creative solutions that benefit both customer and company
        - Be empathetic and understanding of customer frustrations
        - Explain policies clearly and offer alternatives when possible
        - Know when to make exceptions and when to escalate
        - Document all resolutions for future reference
        
        Use policy information and order tools to provide appropriate solutions.
        Focus on turning negative experiences into positive outcomes whenever possible.
        """
    
    async def process_request(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process solution requests for customer issues."""
        try:
            tool_results = []
            tools_used = []
            
            # Determine the type of solution needed
            solution_type = self._classify_solution_type(user_message)
            
            if solution_type == "return":
                await self._handle_return_request(user_message, context, tool_results, tools_used)
            
            elif solution_type == "exchange":
                await self._handle_exchange_request(user_message, context, tool_results, tools_used)
            
            elif solution_type == "compensation":
                await self._handle_compensation_request(user_message, context, tool_results, tools_used)
            
            elif solution_type == "warranty_claim":
                await self._handle_warranty_claim(user_message, context, tool_results, tools_used)
            
            elif solution_type == "general_resolution":
                await self._handle_general_resolution(user_message, context, tool_results, tools_used)
            
            # Generate AI response with context and tool results
            agent_response = await self.generate_response(
                user_message,
                {**context, "tool_results": tool_results, "solution_type": solution_type},
                tools_used
            )
            
            return self.format_final_response(agent_response, tool_results)
            
        except Exception as e:
            logger.error(f"Error in SolutionsAgent.process_request: {e}")
            return {
                "response": "I understand you need help resolving an issue. I'm here to find the best solution for your situation. Could you please provide more details about what happened?",
                "agent_used": self.agent_type,
                "tools_used": [],
                "tool_results": [],
                "confidence": 0.4,
                "thinking_process": f"Error occurred while processing solution request: {str(e)}"
            }
    
    async def _handle_return_request(self, message: str, context: Dict[str, Any], 
                                   tool_results: List[Dict], tools_used: List[str]):
        """Handle return requests."""
        # Get return policy information
        return_reason = self._extract_return_reason(message)
        return_guidelines = await knowledge_tools.get_return_guidelines(return_reason)
        
        tool_results.append({
            "tool": "get_return_guidelines",
            "result": return_guidelines
        })
        tools_used.append("return_policy_lookup")
        
        # If order ID is available, process the return
        order_id = self._extract_order_id(message, context)
        if order_id:
            return_result = await order_tools.initiate_return(order_id, return_reason)
            tool_results.append({
                "tool": "initiate_return",
                "result": return_result
            })
            tools_used.append("return_processing")
    
    async def _handle_exchange_request(self, message: str, context: Dict[str, Any],
                                     tool_results: List[Dict], tools_used: List[str]):
        """Handle exchange requests."""
        # Get exchange policy
        exchange_policy = await knowledge_tools.get_policies("exchange")
        tool_results.append({
            "tool": "get_policies",
            "result": exchange_policy
        })
        tools_used.append("exchange_policy_lookup")
        
        # Check order eligibility if order ID available
        order_id = self._extract_order_id(message, context)
        if order_id:
            order_info = await order_tools.get_order_info(order_id)
            if order_info:
                tool_results.append({
                    "tool": "get_order_info",
                    "result": order_info
                })
                tools_used.append("order_verification")
    
    async def _handle_compensation_request(self, message: str, context: Dict[str, Any],
                                         tool_results: List[Dict], tools_used: List[str]):
        """Handle compensation and goodwill requests."""
        # Determine compensation type and amount
        compensation_info = self._assess_compensation(message, context)
        tool_results.append({
            "tool": "assess_compensation",
            "result": compensation_info
        })
        tools_used.append("compensation_assessment")
    
    async def _handle_warranty_claim(self, message: str, context: Dict[str, Any],
                                   tool_results: List[Dict], tools_used: List[str]):
        """Handle warranty claims."""
        # Get warranty coverage information
        warranty_type = self._extract_warranty_type(message, context)
        warranty_coverage = await knowledge_tools.get_warranty_coverage(warranty_type)
        
        tool_results.append({
            "tool": "get_warranty_coverage",
            "result": warranty_coverage
        })
        tools_used.append("warranty_policy_lookup")
        
        # Check warranty status if order ID available
        order_id = self._extract_order_id(message, context)
        if order_id:
            warranty_status = await order_tools.check_warranty(order_id)
            tool_results.append({
                "tool": "check_warranty",
                "result": warranty_status
            })
            tools_used.append("warranty_verification")
    
    async def _handle_general_resolution(self, message: str, context: Dict[str, Any],
                                       tool_results: List[Dict], tools_used: List[str]):
        """Handle general problem resolution."""
        # Generate resolution options based on the issue
        resolution_options = self._generate_resolution_options(message, context)
        tool_results.append({
            "tool": "generate_resolution_options",
            "result": resolution_options
        })
        tools_used.append("resolution_planning")
    
    def _classify_solution_type(self, message: str) -> str:
        """Classify the type of solution needed."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["return", "send back", "give back"]):
            return "return"
        elif any(word in message_lower for word in ["exchange", "swap", "different", "replace with"]):
            return "exchange"
        elif any(word in message_lower for word in ["refund", "money back", "compensation", "credit"]):
            return "compensation"
        elif any(word in message_lower for word in ["warranty", "repair", "fix", "covered"]):
            return "warranty_claim"
        else:
            return "general_resolution"
    
    def _extract_return_reason(self, message: str) -> str:
        """Extract the reason for return from the message."""
        message_lower = message.lower()
        
        reason_keywords = {
            "defective": ["defective", "broken", "not working", "doesn't work", "won't turn on", "faulty"],
            "damaged_shipping": ["damaged", "broken in shipping", "arrived broken"],
            "wrong_item": ["wrong", "incorrect", "not what I ordered"],
            "size_issue": ["size", "too big", "too small", "doesn't fit"],
            "performance_issue": ["slow", "performance", "not fast enough"],
            "customer_preference": ["changed mind", "don't like", "don't need", "different color"]
        }
        
        for reason, keywords in reason_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return reason
        
        return "other"
    
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
            return context["orders_discussed"][-1]
        
        return None
    
    def _extract_warranty_type(self, message: str, context: Dict[str, Any]) -> str:
        """Extract warranty type from message or context."""
        # Check for specific warranty mentions
        message_lower = message.lower()
        
        if "extended" in message_lower:
            return "3_year"
        elif "basic" in message_lower:
            return "1_year"
        else:
            return "2_year"  # Default assumption
    
    def _assess_compensation(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess appropriate compensation for the customer issue."""
        issue_severity = self._assess_issue_severity(message)
        
        compensation_options = {
            "low": {
                "type": "store_credit",
                "amount": 25,
                "description": "Store credit for inconvenience"
            },
            "medium": {
                "type": "partial_refund",
                "amount": 50,
                "description": "Partial refund or significant store credit"
            },
            "high": {
                "type": "full_refund_plus",
                "amount": 100,
                "description": "Full refund plus additional compensation"
            }
        }
        
        return {
            "severity": issue_severity,
            "recommended_compensation": compensation_options.get(issue_severity, compensation_options["low"]),
            "justification": f"Based on {issue_severity} severity issue assessment",
            "alternatives": list(compensation_options.values())
        }
    
    def _assess_issue_severity(self, message: str) -> str:
        """Assess the severity of the customer issue."""
        message_lower = message.lower()
        
        high_severity_keywords = ["terrible", "awful", "horrible", "worst", "never again", "lawsuit"]
        medium_severity_keywords = ["frustrated", "disappointed", "upset", "annoyed", "unacceptable"]
        
        if any(keyword in message_lower for keyword in high_severity_keywords):
            return "high"
        elif any(keyword in message_lower for keyword in medium_severity_keywords):
            return "medium"
        else:
            return "low"
    
    def _generate_resolution_options(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resolution options for general issues."""
        issue_type = self._identify_issue_type(message)
        
        resolution_templates = {
            "delivery_delay": [
                "Expedite remaining shipment at no cost",
                "Provide tracking updates every 24 hours",
                "Offer store credit for inconvenience"
            ],
            "product_quality": [
                "Full replacement with expedited shipping",
                "Partial refund while keeping product",
                "Upgrade to higher-tier product at same price"
            ],
            "billing_issue": [
                "Correct billing and issue credit",
                "Waive any late fees or penalties",
                "Provide detailed billing explanation"
            ],
            "service_issue": [
                "Escalate to management for review",
                "Provide direct contact for future issues",
                "Offer goodwill gesture for poor experience"
            ]
        }
        
        return {
            "issue_type": issue_type,
            "resolution_options": resolution_templates.get(issue_type, resolution_templates["service_issue"]),
            "escalation_available": True,
            "manager_approval_needed": issue_type in ["billing_issue", "service_issue"]
        }
    
    def _identify_issue_type(self, message: str) -> str:
        """Identify the type of issue for resolution planning."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["delivery", "shipping", "late", "delayed"]):
            return "delivery_delay"
        elif any(word in message_lower for word in ["quality", "defective", "broken", "poor"]):
            return "product_quality"
        elif any(word in message_lower for word in ["bill", "charge", "payment", "refund"]):
            return "billing_issue"
        else:
            return "service_issue"