"""Product expert agent for product information and recommendations."""

import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from tools.product_tools import product_tools
from tools.search_tools import search_tools

logger = logging.getLogger(__name__)

class ProductAgent(BaseAgent):
    """Specialized agent for product expertise and recommendations."""
    
    def __init__(self):
        super().__init__("product")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the product agent."""
        return """
        You are a Product Expert for a customer service team. Your expertise includes:
        
        - Product specifications and features
        - Product comparisons and recommendations
        - Inventory and availability information
        - Pricing and value analysis
        - Product compatibility and requirements
        - New product releases and updates
        
        Guidelines:
        - Provide accurate and detailed product information
        - Make recommendations based on customer needs and use cases
        - Compare products objectively highlighting pros and cons
        - Consider customer budget and requirements
        - Stay up-to-date with current inventory and pricing
        - Explain technical specifications in customer-friendly terms
        
        Use the product database to provide accurate information and search for current deals when helpful.
        Focus on helping customers make informed decisions that best meet their needs.
        """
    
    async def process_request(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process product-related requests."""
        try:
            tool_results = []
            tools_used = []
            
            # Determine the type of product request
            request_type = self._classify_request_type(user_message)
            
            if request_type == "product_info":
                # Get specific product information
                product_id = self._extract_product_id(user_message, context)
                if product_id:
                    product_info = await product_tools.get_product_info(product_id)
                    if product_info:
                        tool_results.append({
                            "tool": "get_product_info",
                            "result": product_info
                        })
                        tools_used.append("product_lookup")
            
            elif request_type == "comparison":
                # Compare products
                product_ids = self._extract_multiple_products(user_message, context)
                if len(product_ids) >= 2:
                    comparison = await product_tools.compare_products(product_ids)
                    tool_results.append({
                        "tool": "compare_products",
                        "result": comparison
                    })
                    tools_used.append("product_comparison")
            
            elif request_type == "alternatives":
                # Find alternatives
                product_id = self._extract_product_id(user_message, context)
                if product_id:
                    alternatives = await product_tools.get_alternatives(product_id)
                    tool_results.append({
                        "tool": "get_alternatives",
                        "result": alternatives
                    })
                    tools_used.append("alternative_search")
            
            elif request_type == "recommendations":
                # Generate recommendations based on needs
                customer_needs = self._extract_customer_needs(user_message)
                recommendations = await product_tools.get_recommendations(customer_needs)
                tool_results.append({
                    "tool": "get_recommendations",
                    "result": recommendations
                })
                tools_used.append("recommendation_engine")
            
            elif request_type == "availability":
                # Check inventory
                product_id = self._extract_product_id(user_message, context)
                if product_id:
                    inventory = await product_tools.check_inventory(product_id)
                    tool_results.append({
                        "tool": "check_inventory",
                        "result": inventory
                    })
                    tools_used.append("inventory_check")
            
            elif request_type == "deals":
                # Search for deals
                product_category = self._extract_category(user_message)
                deals = await search_tools.find_deals(product_category)
                tool_results.append({
                    "tool": "find_deals",
                    "result": deals
                })
                tools_used.append("deal_search")
            
            # Generate AI response with context and tool results
            agent_response = await self.generate_response(
                user_message,
                {**context, "tool_results": tool_results, "request_type": request_type},
                tools_used
            )
            
            return self.format_final_response(agent_response, tool_results)
            
        except Exception as e:
            logger.error(f"Error in ProductAgent.process_request: {e}")
            return {
                "response": "I'd be happy to help you with product information. Could you please tell me which specific product you're interested in or what you're looking for?",
                "agent_used": self.agent_type,
                "tools_used": [],
                "tool_results": [],
                "confidence": 0.4,
                "thinking_process": f"Error occurred while processing product request: {str(e)}"
            }
    
    def _classify_request_type(self, message: str) -> str:
        """Classify the type of product request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["compare", "comparison", "vs", "versus", "difference"]):
            return "comparison"
        elif any(word in message_lower for word in ["alternative", "similar", "other options", "different"]):
            return "alternatives"
        elif any(word in message_lower for word in ["recommend", "suggest", "best", "which should", "what should"]):
            return "recommendations"
        elif any(word in message_lower for word in ["available", "in stock", "inventory", "how many"]):
            return "availability"
        elif any(word in message_lower for word in ["deal", "sale", "discount", "promotion", "cheaper"]):
            return "deals"
        elif any(word in message_lower for word in ["specs", "specification", "features", "details"]):
            return "product_info"
        else:
            return "general_inquiry"
    
    def _extract_product_id(self, message: str, context: Dict[str, Any]) -> str:
        """Extract product ID from message or context."""
        message_lower = message.lower()
        
        # Map product names to IDs
        product_map = {
            "techbook pro 15": "TB-PRO-15",
            "pro 15": "TB-PRO-15",
            "techbook air 13": "TB-AIR-13", 
            "air 13": "TB-AIR-13",
            "techbook gaming 17": "TB-GAME-17",
            "gaming 17": "TB-GAME-17",
            "techbook basic 14": "TB-BASIC-14",
            "basic 14": "TB-BASIC-14"
        }
        
        for name, product_id in product_map.items():
            if name in message_lower:
                return product_id
        
        # Check context for previously discussed products
        if context.get("products_discussed"):
            # Try to map discussed products to IDs
            for product in context["products_discussed"]:
                for name, product_id in product_map.items():
                    if name in product.lower():
                        return product_id
        
        return None
    
    def _extract_multiple_products(self, message: str, context: Dict[str, Any]) -> List[str]:
        """Extract multiple product IDs for comparison."""
        message_lower = message.lower()
        product_ids = []
        
        # Map product names to IDs
        product_map = {
            "techbook pro 15": "TB-PRO-15",
            "pro 15": "TB-PRO-15",
            "techbook air 13": "TB-AIR-13",
            "air 13": "TB-AIR-13", 
            "techbook gaming 17": "TB-GAME-17",
            "gaming 17": "TB-GAME-17",
            "techbook basic 14": "TB-BASIC-14",
            "basic 14": "TB-BASIC-14"
        }
        
        for name, product_id in product_map.items():
            if name in message_lower:
                product_ids.append(product_id)
        
        # If only one found in message, check context for others
        if len(product_ids) < 2 and context.get("products_discussed"):
            for product in context["products_discussed"]:
                for name, product_id in product_map.items():
                    if name in product.lower() and product_id not in product_ids:
                        product_ids.append(product_id)
                        if len(product_ids) >= 2:
                            break
        
        return product_ids
    
    def _extract_customer_needs(self, message: str) -> Dict[str, Any]:
        """Extract customer needs and preferences from message."""
        message_lower = message.lower()
        needs = {}
        
        # Extract budget
        import re
        budget_match = re.search(r'\$?(\d+)', message)
        if budget_match:
            needs["max_budget"] = float(budget_match.group(1))
        
        # Extract use case
        use_cases = {
            "gaming": ["gaming", "games", "play", "gamer"],
            "business": ["business", "work", "office", "professional"],
            "student": ["student", "school", "study", "education"],
            "travel": ["travel", "portable", "light", "lightweight"]
        }
        
        for use_case, keywords in use_cases.items():
            if any(keyword in message_lower for keyword in keywords):
                needs["use_case"] = use_case
                break
        
        # Extract category preference
        categories = {
            "professional": ["professional", "business", "work"],
            "gaming": ["gaming", "games"],
            "ultrabook": ["thin", "light", "portable", "ultrabook"],
            "budget": ["cheap", "affordable", "budget", "basic"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                needs["preferred_category"] = category
                break
        
        return needs
    
    def _extract_category(self, message: str) -> str:
        """Extract product category for deal search."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["laptop", "computer", "notebook"]):
            return "laptops"
        elif "techbook" in message_lower:
            return "techbook laptops"
        else:
            return "electronics"