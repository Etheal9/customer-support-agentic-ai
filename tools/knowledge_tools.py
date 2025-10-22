"""Knowledge base and policy tools for customer support."""

import logging
from typing import List, Dict, Any, Optional
from data.mock_data import search_knowledge_base, get_policy

logger = logging.getLogger(__name__)

class KnowledgeTools:
    """Tools for accessing knowledge base and company policies."""
    
    async def search_knowledge(self, issue: str) -> List[str]:
        """Search knowledge base for troubleshooting steps."""
        try:
            steps = search_knowledge_base(issue)
            
            if steps:
                logger.info(f"Found {len(steps)} troubleshooting steps for: {issue}")
                return steps
            else:
                # Fallback to general advice
                general_steps = [
                    "Restart the device and try again",
                    "Check all cable connections",
                    "Update device drivers and software",
                    "Contact technical support if issue persists"
                ]
                logger.info(f"No specific steps found for '{issue}', returning general advice")
                return general_steps
                
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ["Please contact technical support for assistance"]
    
    async def get_policies(self, policy_type: str) -> Dict[str, Any]:
        """Retrieve company policy information."""
        try:
            policy = get_policy(policy_type)
            
            if policy:
                logger.info(f"Retrieved {policy_type} policy")
                return policy
            else:
                logger.warning(f"Policy type '{policy_type}' not found")
                return {"error": f"Policy type '{policy_type}' not found"}
                
        except Exception as e:
            logger.error(f"Error retrieving policy {policy_type}: {e}")
            return {"error": str(e)}
    
    async def get_troubleshooting_guide(self, device_type: str, issue: str) -> Dict[str, Any]:
        """Get comprehensive troubleshooting guide for specific device and issue."""
        try:
            # Combine device type and issue for more specific search
            search_query = f"{device_type} {issue}"
            basic_steps = await self.search_knowledge(search_query)
            
            # Add device-specific information
            device_info = self._get_device_specific_info(device_type)
            
            guide = {
                "device_type": device_type,
                "issue": issue,
                "basic_troubleshooting": basic_steps,
                "device_specific_tips": device_info.get("tips", []),
                "common_causes": device_info.get("common_causes", []),
                "when_to_escalate": [
                    "Issue persists after following all troubleshooting steps",
                    "Device shows signs of physical damage",
                    "Multiple attempts at basic fixes have failed",
                    "Customer reports unusual sounds, smells, or excessive heat"
                ],
                "escalation_process": [
                    "Document all troubleshooting steps attempted",
                    "Gather device information (model, warranty status)",
                    "Create technical support ticket",
                    "Schedule callback or in-person service if needed"
                ]
            }
            
            logger.info(f"Generated troubleshooting guide for {device_type} - {issue}")
            return guide
            
        except Exception as e:
            logger.error(f"Error creating troubleshooting guide: {e}")
            return {"error": str(e)}
    
    async def get_warranty_coverage(self, warranty_type: str) -> Dict[str, Any]:
        """Get detailed warranty coverage information."""
        try:
            warranty_policy = await self.get_policies("warranty")
            
            if "error" in warranty_policy:
                return warranty_policy
            
            coverage_info = {
                "warranty_type": warranty_type,
                "coverage_details": warranty_policy["coverage"],
                "exclusions": warranty_policy["exclusions"],
                "claim_process": warranty_policy["process"],
                "tips": [
                    "Keep original receipt and warranty documentation",
                    "Register product within 30 days of purchase",
                    "Perform regular maintenance as recommended",
                    "Report issues as soon as they occur"
                ]
            }
            
            logger.info(f"Retrieved warranty coverage for {warranty_type}")
            return coverage_info
            
        except Exception as e:
            logger.error(f"Error getting warranty coverage: {e}")
            return {"error": str(e)}
    
    async def get_return_guidelines(self, reason: str) -> Dict[str, Any]:
        """Get specific return guidelines based on return reason."""
        try:
            return_policy = await self.get_policies("return")
            
            if "error" in return_policy:
                return return_policy
            
            # Determine if return reason qualifies for free return
            free_return = reason.lower() in return_policy["free_return_reasons"]
            
            guidelines = {
                "return_reason": reason,
                "is_free_return": free_return,
                "return_period": f"{return_policy['period_days']} days",
                "condition_requirements": return_policy["condition"],
                "restocking_fee": 0 if free_return else return_policy["restocking_fee"],
                "process_steps": return_policy["process"],
                "preparation_tips": [
                    "Ensure item is in original condition",
                    "Include all original accessories and packaging",
                    "Clean the item before returning",
                    "Remove all personal data from electronic devices"
                ]
            }
            
            logger.info(f"Generated return guidelines for reason: {reason}")
            return guidelines
            
        except Exception as e:
            logger.error(f"Error getting return guidelines: {e}")
            return {"error": str(e)}
    
    async def search_faq(self, question: str) -> Dict[str, Any]:
        """Search frequently asked questions."""
        try:
            # Simplified FAQ search - in real implementation, this would use NLP
            question_lower = question.lower()
            
            faq_responses = {
                "shipping": {
                    "question": "How long does shipping take?",
                    "answer": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days. Free shipping is available on orders over $500."
                },
                "payment": {
                    "question": "What payment methods do you accept?",
                    "answer": "We accept all major credit cards, PayPal, Apple Pay, and bank transfers. Payment plans are available for purchases over $1000."
                },
                "warranty": {
                    "question": "How does the warranty work?",
                    "answer": "Warranty period varies by product (1-3 years). Covers manufacturing defects and hardware failures. Registration required within 30 days."
                },
                "support": {
                    "question": "How can I contact support?",
                    "answer": "Support is available 24/7 via chat, email, or phone. For technical issues, our specialist team is available Mon-Fri 8AM-8PM."
                }
            }
            
            # Find matching FAQ
            for key, faq in faq_responses.items():
                if key in question_lower:
                    logger.info(f"Found FAQ match for: {question}")
                    return faq
            
            # No direct match found
            logger.info(f"No FAQ match found for: {question}")
            return {
                "question": question,
                "answer": "I don't have a specific FAQ for that question, but I can help you find the information you need. Could you provide more details about what you're looking for?"
            }
            
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return {"error": str(e)}
    
    def _get_device_specific_info(self, device_type: str) -> Dict[str, Any]:
        """Get device-specific troubleshooting information."""
        device_guides = {
            "laptop": {
                "tips": [
                    "Check power adapter LED indicator",
                    "Try removing battery for 30 seconds",
                    "Ensure proper ventilation around device",
                    "Check for Windows updates and driver updates"
                ],
                "common_causes": [
                    "Power adapter failure",
                    "Battery degradation",
                    "Overheating due to dust buildup",
                    "Software conflicts or outdated drivers"
                ]
            },
            "techbook": {
                "tips": [
                    "Use TechBook diagnostic tool in BIOS",
                    "Check TechBook support portal for device-specific guides",
                    "Ensure latest TechBook software is installed",
                    "Review TechBook maintenance schedule"
                ],
                "common_causes": [
                    "Firmware outdated",
                    "TechBook-specific driver issues",
                    "Hardware compatibility problems",
                    "Thermal management issues"
                ]
            }
        }
        
        return device_guides.get(device_type.lower(), device_guides["laptop"])

# Global knowledge tools instance
knowledge_tools = KnowledgeTools()