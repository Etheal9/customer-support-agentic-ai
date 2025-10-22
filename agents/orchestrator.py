"""Orchestrator agent that coordinates all specialist agents."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.order_agent import OrderAgent
from agents.tech_support_agent import TechSupportAgent
from agents.product_agent import ProductAgent
from agents.solutions_agent import SolutionsAgent
from planning.planner import planner, ExecutionPlan, ExecutionMode
from memory.session_memory import memory

logger = logging.getLogger(__name__)

class Orchestrator(BaseAgent):
    """Main orchestrator that coordinates all specialist agents."""
    
    def __init__(self):
        super().__init__("orchestrator")
        
        # Initialize specialist agents
        self.agents = {
            "order": OrderAgent(),
            "tech_support": TechSupportAgent(),
            "product": ProductAgent(),
            "solutions": SolutionsAgent()
        }
        
        logger.info("Orchestrator initialized with all specialist agents")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the orchestrator."""
        return """
        You are the Orchestrator for a multi-agent customer service system. Your role is to:
        
        - Coordinate multiple specialist agents to provide comprehensive customer support
        - Synthesize responses from different agents into coherent, helpful answers
        - Ensure all aspects of customer requests are addressed
        - Maintain conversation flow and context across agent interactions
        - Escalate complex issues when appropriate
        
        Guidelines:
        - Present unified responses that feel natural, not like multiple agents responded
        - Prioritize the most relevant information for the customer
        - Ensure all customer questions are answered completely
        - Maintain empathetic and professional tone throughout
        - Reference specific order numbers, products, or issues when relevant
        
        You coordinate with these specialists:
        - Order Agent: Order tracking, modifications, returns, warranty
        - Tech Support Agent: Technical troubleshooting and problem resolution
        - Product Agent: Product information, comparisons, recommendations
        - Solutions Agent: Returns, exchanges, compensation, problem resolution
        
        Synthesize their responses into a single, coherent customer response.
        """
    
    async def process_request(self, user_message: str, session_id: str) -> Dict[str, Any]:
        """Process a customer request by coordinating specialist agents."""
        try:
            start_time = datetime.now()
            
            # Ensure session exists and get context
            session_id, session = memory.get_or_create_session(session_id)
            context = memory.get_context_for_agents(session_id)
            

            
            # Create execution plan
            logger.info(f"Creating plan for request: {user_message[:50]}...")
            plan = await planner.create_plan(user_message, context)
            
            # Validate plan
            is_valid, validation_issues = await planner.validate_plan(plan)
            if not is_valid:
                logger.warning(f"Plan validation failed: {validation_issues}")
                return await self._handle_invalid_plan(user_message, context, validation_issues)
            
            # Execute plan
            logger.info(f"Executing plan {plan.plan_id} with {len(plan.steps)} steps in {plan.execution_mode.value} mode")
            execution_results = await self._execute_plan(plan, user_message, context)
            
            # Synthesize final response
            final_response = await self._synthesize_response(
                user_message, execution_results, plan, context
            )
            
            # Update memory
            memory.add_message(
                session_id, 
                "user", 
                user_message
            )
            memory.add_message(
                session_id,
                "assistant",
                final_response["response"],
                agent_used="orchestrator",
                tools_used=final_response.get("tools_used", []),
                plan_executed=final_response.get("plan_executed")
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            final_response["execution_time"] = execution_time
            
            logger.info(f"Request processed successfully in {execution_time:.2f}s")
            return final_response
            
        except Exception as e:
            logger.error(f"Error in orchestrator process_request: {e}")
            return await self._handle_error(user_message, str(e))
    
    async def _execute_plan(self, plan: ExecutionPlan, user_message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the plan and return results from all agents."""
        results = []
        
        if plan.execution_mode == ExecutionMode.PARALLEL:
            # Execute all steps in parallel
            tasks = []
            for step in plan.steps:
                if step.agent_type in self.agents:
                    task = asyncio.create_task(
                        self.agents[step.agent_type].process_request(user_message, context)
                    )
                    tasks.append((step, task))
            
            # Wait for all tasks to complete
            for step, task in tasks:
                try:
                    step.status = "running"
                    result = await task
                    step.status = "completed"
                    step.result = result
                    results.append(result)
                except Exception as e:
                    step.status = "failed"
                    logger.error(f"Step {step.agent_type} failed: {e}")
                    results.append({
                        "response": f"Error in {step.agent_type} agent",
                        "agent_used": step.agent_type,
                        "error": str(e)
                    })
        
        elif plan.execution_mode == ExecutionMode.SEQUENTIAL:
            # Execute steps sequentially
            accumulated_context = context.copy()
            
            for step in plan.steps:
                if step.agent_type in self.agents:
                    try:
                        step.status = "running"
                        logger.info(f"Executing step: {step.agent_type}")
                        
                        result = await self.agents[step.agent_type].process_request(
                            user_message, accumulated_context
                        )
                        
                        step.status = "completed"
                        step.result = result
                        results.append(result)
                        
                        # Update context with results for next step
                        if result.get("tool_results"):
                            accumulated_context["previous_results"] = result["tool_results"]
                        
                    except Exception as e:
                        step.status = "failed"
                        logger.error(f"Step {step.agent_type} failed: {e}")
                        results.append({
                            "response": f"Error in {step.agent_type} agent",
                            "agent_used": step.agent_type,
                            "error": str(e)
                        })
        
        elif plan.execution_mode == ExecutionMode.CONDITIONAL:
            # Execute steps based on dependencies
            completed_agents = set()
            accumulated_context = context.copy()
            
            while len(completed_agents) < len(plan.steps):
                progress_made = False
                
                for step in plan.steps:
                    if (step.agent_type not in completed_agents and 
                        all(dep in completed_agents for dep in step.depends_on)):
                        
                        try:
                            step.status = "running"
                            logger.info(f"Executing conditional step: {step.agent_type}")
                            
                            result = await self.agents[step.agent_type].process_request(
                                user_message, accumulated_context
                            )
                            
                            step.status = "completed"
                            step.result = result
                            results.append(result)
                            completed_agents.add(step.agent_type)
                            progress_made = True
                            
                            # Update context
                            if result.get("tool_results"):
                                accumulated_context["previous_results"] = result["tool_results"]
                            
                        except Exception as e:
                            step.status = "failed"
                            logger.error(f"Conditional step {step.agent_type} failed: {e}")
                            completed_agents.add(step.agent_type)  # Mark as completed to avoid infinite loop
                            progress_made = True
                
                if not progress_made:
                    logger.error("No progress made in conditional execution - breaking loop")
                    break
        
        plan.status = "completed"
        return results
    
    async def _synthesize_response(self, user_message: str, agent_results: List[Dict[str, Any]], 
                                 plan: ExecutionPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into a coherent answer."""
        try:
            # Prepare synthesis context
            synthesis_context = {
                "user_request": user_message,
                "agent_responses": [
                    {
                        "agent": result.get("agent_used", "unknown"),
                        "response": result.get("response", ""),
                        "confidence": result.get("confidence", 0.5),
                        "tools_used": result.get("tools_used", [])
                    }
                    for result in agent_results if result.get("response")
                ],
                "plan_info": {
                    "execution_mode": plan.execution_mode.value,
                    "steps_completed": len([s for s in plan.steps if s.status == "completed"]),
                    "total_steps": len(plan.steps)
                }
            }
            
            # Generate synthesized response using AI
            synthesis_prompt = self._create_synthesis_prompt(synthesis_context)
            synthesis_response = await self.generate_response(
                synthesis_prompt, 
                {**context, "synthesis_context": synthesis_context}
            )
            
            # Compile comprehensive response
            all_tools_used = []
            all_tool_results = []
            
            for result in agent_results:
                all_tools_used.extend(result.get("tools_used", []))
                all_tool_results.extend(result.get("tool_results", []))
            
            return {
                "response": synthesis_response["response"],
                "plan_executed": {
                    "plan_id": plan.plan_id,
                    "execution_mode": plan.execution_mode.value,
                    "steps": [
                        {
                            "agent": step.agent_type,
                            "status": step.status,
                            "task": step.task_description
                        }
                        for step in plan.steps
                    ],
                    "agents_involved": list(set(result.get("agent_used") for result in agent_results if result.get("agent_used"))),
                    "tools_used": list(set(all_tools_used)),
                    "estimated_time": plan.estimated_time,
                    "actual_steps": len(agent_results)
                },
                "thinking_process": f"Coordinated {len(agent_results)} specialist agents using {plan.execution_mode.value} execution",
                "confidence": min(synthesis_response.get("confidence", 0.7), max(r.get("confidence", 0.5) for r in agent_results) if agent_results else 0.5),
                "tools_used": list(set(all_tools_used)),
                "tool_results": all_tool_results
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            return await self._create_fallback_response(agent_results)
    
    def _create_synthesis_prompt(self, synthesis_context: Dict[str, Any]) -> str:
        """Create a prompt for synthesizing multiple agent responses."""
        prompt = f"Customer Request: {synthesis_context['user_request']}\n\n"
        prompt += "Specialist Agent Responses:\n"
        
        for i, response_info in enumerate(synthesis_context['agent_responses'], 1):
            prompt += f"{i}. {response_info['agent'].title()} Agent: {response_info['response']}\n\n"
        
        prompt += """
        Please synthesize these specialist responses into a single, coherent customer service response that:
        - Addresses all aspects of the customer's request
        - Flows naturally as if from one knowledgeable representative
        - Prioritizes the most important information for the customer
        - Maintains a helpful and professional tone
        - Includes specific details (order numbers, product names, etc.) when relevant
        
        Provide a unified response that feels natural and complete.
        """
        
        return prompt
    
    async def _create_fallback_response(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a fallback response when synthesis fails."""
        if not agent_results:
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team directly.",
                "plan_executed": {"error": "No agent results available"},
                "confidence": 0.3,
                "thinking_process": "Fallback response due to missing agent results"
            }
        
        # Use the response from the agent with highest confidence
        best_result = max(agent_results, key=lambda x: x.get("confidence", 0))
        
        return {
            "response": best_result.get("response", "I'm here to help with your request."),
            "plan_executed": {"fallback": True, "source_agent": best_result.get("agent_used")},
            "confidence": best_result.get("confidence", 0.5),
            "thinking_process": "Used fallback response from best-performing agent"
        }
    
    async def _handle_invalid_plan(self, user_message: str, context: Dict[str, Any], 
                                 validation_issues: List[str]) -> Dict[str, Any]:
        """Handle cases where plan validation fails."""
        logger.warning(f"Using fallback execution due to invalid plan: {validation_issues}")
        
        # Try a simple single-agent approach
        try:
            # Default to tech support for most issues
            agent = self.agents["tech_support"]
            result = await agent.process_request(user_message, context)
            
            return {
                "response": result.get("response", "I'm here to help with your request."),
                "plan_executed": {
                    "fallback": True,
                    "reason": "Plan validation failed",
                    "issues": validation_issues
                },
                "confidence": 0.6,
                "thinking_process": "Used fallback single-agent execution"
            }
            
        except Exception as e:
            logger.error(f"Fallback execution also failed: {e}")
            return await self._handle_error(user_message, str(e))
    


    async def _handle_error(self, user_message: str, error: str) -> Dict[str, Any]:
        """Handle errors in request processing."""
        return {
            "response": "I apologize, but I'm experiencing technical difficulties right now. Please try rephrasing your question or contact our support team directly for immediate assistance.",
            "plan_executed": {"error": error},
            "confidence": 0.2,
            "thinking_process": f"Error handling activated due to: {error}",
            "error": error
        }

# Global orchestrator instance
orchestrator = Orchestrator()