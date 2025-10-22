"""Order management tools for customer service operations."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from data.mock_data import get_order, get_policy

logger = logging.getLogger(__name__)

class OrderTools:
    """Tools for order management and tracking."""
    
    async def get_order_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve comprehensive order information."""
        try:
            order = get_order(order_id)
            if not order:
                return None
            
            # Add calculated fields
            order_info = order.copy()
            order_info["order_age_days"] = self._calculate_order_age(order["order_date"])
            order_info["warranty_status"] = self._check_warranty_status(order)
            order_info["return_eligible"] = self._check_return_eligibility(order)
            
            logger.info(f"Retrieved order info for {order_id}")
            return order_info
            
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {e}")
            return None
    
    async def check_warranty(self, order_id: str) -> Dict[str, Any]:
        """Check warranty status for an order."""
        try:
            order = get_order(order_id)
            if not order:
                return {"error": "Order not found"}
            
            warranty_info = self._check_warranty_status(order)
            
            # Get warranty policy details
            policy = get_policy("warranty")
            warranty_period = order.get("warranty", "1 year")
            
            result = {
                "order_id": order_id,
                "warranty_period": warranty_period,
                "warranty_expires": order.get("warranty_expires"),
                "is_active": warranty_info["is_active"],
                "days_remaining": warranty_info["days_remaining"],
                "coverage": policy["coverage"].get(warranty_period.replace(" ", "_"), []),
                "exclusions": policy["exclusions"]
            }
            
            logger.info(f"Checked warranty for order {order_id}: {warranty_info['is_active']}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking warranty for {order_id}: {e}")
            return {"error": str(e)}
    
    async def initiate_return(self, order_id: str, reason: str) -> Dict[str, Any]:
        """Initiate the return process for an order."""
        try:
            order = get_order(order_id)
            if not order:
                return {"error": "Order not found"}
            
            # Check return eligibility
            eligibility = self._check_return_eligibility(order)
            if not eligibility["eligible"]:
                return {
                    "error": "Return not eligible",
                    "reason": eligibility["reason"]
                }
            
            # Get return policy
            policy = get_policy("return")
            
            # Generate return authorization
            auth_number = f"RMA-{order_id}-{datetime.now().strftime('%Y%m%d')}"
            
            # Determine if restocking fee applies
            free_return = reason.lower() in policy["free_return_reasons"]
            restocking_fee = 0 if free_return else order["price"] * policy["restocking_fee"]
            
            result = {
                "authorization_number": auth_number,
                "order_id": order_id,
                "reason": reason,
                "return_deadline": eligibility["deadline"],
                "restocking_fee": restocking_fee,
                "free_return": free_return,
                "process_steps": policy["process"],
                "estimated_refund": order["price"] - restocking_fee
            }
            
            logger.info(f"Initiated return for order {order_id} with RMA {auth_number}")
            return result
            
        except Exception as e:
            logger.error(f"Error initiating return for {order_id}: {e}")
            return {"error": str(e)}
    
    async def track_shipment(self, order_id: str) -> Dict[str, Any]:
        """Get shipment tracking information."""
        try:
            order = get_order(order_id)
            if not order:
                return {"error": "Order not found"}
            
            # Mock tracking information
            tracking_info = {
                "order_id": order_id,
                "status": order["status"],
                "tracking_number": f"TRK{order_id}2024",
                "carrier": "FastShip Express",
                "shipped_date": order.get("order_date"),
                "expected_delivery": order.get("delivery_date"),
                "current_location": self._get_mock_location(order["status"]),
                "delivery_attempts": 0 if order["status"] != "delivered" else 1
            }
            
            # Add status-specific information
            if order["status"] == "delivered":
                tracking_info["delivered_date"] = order["delivery_date"]
                tracking_info["signed_by"] = "Resident"
            elif order["status"] == "shipped":
                tracking_info["estimated_delivery"] = order["delivery_date"]
                tracking_info["in_transit"] = True
            
            logger.info(f"Retrieved tracking info for order {order_id}")
            return tracking_info
            
        except Exception as e:
            logger.error(f"Error tracking shipment for {order_id}: {e}")
            return {"error": str(e)}
    
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to modify an existing order."""
        try:
            order = get_order(order_id)
            if not order:
                return {"error": "Order not found"}
            
            # Check if order can be modified
            if order["status"] in ["shipped", "delivered"]:
                return {
                    "error": "Cannot modify order",
                    "reason": f"Order is already {order['status']}"
                }
            
            # For demo purposes, return success with modifications
            result = {
                "order_id": order_id,
                "status": "modification_requested",
                "requested_changes": modifications,
                "processing_time": "1-2 business days",
                "confirmation_needed": True
            }
            
            logger.info(f"Modification requested for order {order_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error modifying order {order_id}: {e}")
            return {"error": str(e)}
    
    def _calculate_order_age(self, order_date: str) -> int:
        """Calculate the age of an order in days."""
        try:
            order_dt = datetime.strptime(order_date, "%Y-%m-%d")
            return (datetime.now() - order_dt).days
        except:
            return 0
    
    def _check_warranty_status(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Check if warranty is still active."""
        try:
            warranty_expires = order.get("warranty_expires")
            if not warranty_expires:
                return {"is_active": False, "days_remaining": 0}
            
            expire_date = datetime.strptime(warranty_expires, "%Y-%m-%d")
            days_remaining = (expire_date - datetime.now()).days
            
            return {
                "is_active": days_remaining > 0,
                "days_remaining": max(0, days_remaining)
            }
        except:
            return {"is_active": False, "days_remaining": 0}
    
    def _check_return_eligibility(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Check if order is eligible for return."""
        try:
            order_age = self._calculate_order_age(order["order_date"])
            policy = get_policy("return")
            
            if order_age > policy["period_days"]:
                return {
                    "eligible": False,
                    "reason": f"Return period expired ({policy['period_days']} days)"
                }
            
            if order["status"] != "delivered":
                return {
                    "eligible": False,
                    "reason": "Order must be delivered before return"
                }
            
            # Calculate deadline
            order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            deadline = order_date + timedelta(days=policy["period_days"])
            
            return {
                "eligible": True,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "days_remaining": policy["period_days"] - order_age
            }
            
        except Exception as e:
            logger.error(f"Error checking return eligibility: {e}")
            return {"eligible": False, "reason": "Unable to determine eligibility"}
    
    def _get_mock_location(self, status: str) -> str:
        """Get mock current location based on order status."""
        locations = {
            "processing": "Fulfillment Center",
            "shipped": "In Transit - Regional Hub",
            "delivered": "Delivered to Address"
        }
        return locations.get(status, "Unknown")

# Global order tools instance
order_tools = OrderTools()