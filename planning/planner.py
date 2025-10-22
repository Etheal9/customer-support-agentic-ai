"""Planning module for coordinating multi-agent responses."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Execution modes for agent coordination."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

class PlanStep:
    """Represents a single step in an execution plan."""
    
    def __init__(self, agent_type: str, task_description: str, priority: int = 1, 
                 depends_on: List[str] = None, tools_required: List[str] = None):
        self.agent_type = agent_type
        self.task_description = task_description
        self.priority = priority
        self.depends_on = depends_on or []
        self.tools_required = tools_required or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.execution_time = None

class ExecutionPlan:
    """Represents a complete execution plan for handling a customer request."""
    
    def __init__(self, request: str, plan_id: str):
        self.request = request
        self.plan_id = plan_id
        self.steps: List[PlanStep] = []
        self.execution_mode = ExecutionMode.SEQUENTIAL
        self.estimated_time = 0
        self.confidence = 0.0
        self.created_at = None
        self.status = "created"  # created, executing, completed, failed

class Planner:
    """Creates and validates execution plans for customer requests."""
    
    def __init__(self):
        self.agent_capabilities = {
            "order": {
                "keywords": ["order", "tracking", "delivery", "shipping", "return", "refund", "warranty"],
                "tools": ["order_tools", "tracking"],
                "priority": 1
            },
            "tech_support": {
                "keywords": ["not working", "broken", "fix", "troubleshoot", "support", "help", "issue", "problem"],
                "tools": ["knowledge_tools", "search_tools"],
                "priority": 2
            },
            "product": {
                "keywords": ["specs", "compare", "recommend", "alternative", "price", "features", "which", "best"],
                "tools": ["product_tools", "search_tools"],
                "priority": 2
            },
            "solutions": {
                "keywords": ["disappointed", "unsatisfied", "compensation", "exchange", "solution", "resolve"],
                "tools": ["knowledge_tools", "order_tools"],
                "priority": 3
            }
        }
    
    async def create_plan(self, user_request: str, context: Dict[str, Any]) -> ExecutionPlan:
        """Create an execution plan for the user request."""
        try:
            plan_id = self._generate_plan_id()
            plan = ExecutionPlan(user_request, plan_id)
            
            # Analyze the request to determine required agents
            required_agents = self._analyze_request(user_request, context)
            
            # Create plan steps based on request complexity
            if len(required_agents) == 1:
                # Simple single-agent request
                plan.execution_mode = ExecutionMode.SEQUENTIAL
                plan.steps = [self._create_step(required_agents[0], user_request)]
            
            elif self._is_complex_request(user_request):
                # Complex multi-agent request
                plan.execution_mode = ExecutionMode.CONDITIONAL
                plan.steps = await self._create_complex_plan(user_request, required_agents, context)
            
            else:
                # Multi-agent request that can run in parallel
                plan.execution_mode = ExecutionMode.PARALLEL
                plan.steps = [self._create_step(agent, user_request) for agent in required_agents]
            
            # Calculate estimates
            plan.estimated_time = self._estimate_execution_time(plan.steps)
            plan.confidence = self._estimate_plan_confidence(plan.steps, context)
            plan.status = "ready"
            
            logger.info(f"Created plan {plan_id} with {len(plan.steps)} steps, mode: {plan.execution_mode.value}")
            return plan
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            # Return a fallback plan
            return self._create_fallback_plan(user_request)
    
    async def validate_plan(self, plan: ExecutionPlan) -> Tuple[bool, List[str]]:
        """Validate an execution plan and return any issues."""
        issues = []
        
        # Check if plan has steps
        if not plan.steps:
            issues.append("Plan has no execution steps")
        
        # Check for dependency conflicts
        for step in plan.steps:
            for dependency in step.depends_on:
                if not any(s.agent_type == dependency for s in plan.steps):
                    issues.append(f"Step {step.agent_type} depends on {dependency} which is not in the plan")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan.steps):
            issues.append("Plan has circular dependencies")
        
        # Validate tool requirements
        for step in plan.steps:
            available_tools = self.agent_capabilities.get(step.agent_type, {}).get("tools", [])
            for tool in step.tools_required:
                if tool not in available_tools:
                    issues.append(f"Agent {step.agent_type} requires unavailable tool: {tool}")
        
        is_valid = len(issues) == 0
        logger.info(f"Plan validation: {'PASSED' if is_valid else 'FAILED'} with {len(issues)} issues")
        
        return is_valid, issues
    
    def _analyze_request(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Analyze the request to determine which agents are needed."""
        request_lower = request.lower()
        required_agents = []
        agent_scores = {}
        
        # Score each agent based on keyword matches
        for agent_type, capabilities in self.agent_capabilities.items():
            score = 0
            for keyword in capabilities["keywords"]:
                if keyword in request_lower:
                    score += 1
            
            # Boost score based on context
            if agent_type == "order" and context.get("orders_discussed"):
                score += 2
            if agent_type == "product" and context.get("products_discussed"):
                score += 1
            
            agent_scores[agent_type] = score
        
        # Select agents with scores above threshold
        threshold = 0
        for agent_type, score in agent_scores.items():
            if score > threshold:
                required_agents.append(agent_type)
        
        # Ensure at least one agent is selected
        if not required_agents:
            # Default to the agent with highest score
            best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]
            required_agents.append(best_agent)
        
        # Sort by priority
        required_agents.sort(key=lambda x: self.agent_capabilities[x]["priority"])
        
        logger.info(f"Request analysis selected agents: {required_agents}")
        return required_agents
    
    def _create_step(self, agent_type: str, request: str, priority: int = 1) -> PlanStep:
        """Create a plan step for an agent."""
        capabilities = self.agent_capabilities.get(agent_type, {})
        
        return PlanStep(
            agent_type=agent_type,
            task_description=f"Process {agent_type} aspects of: {request}",
            priority=priority,
            tools_required=capabilities.get("tools", [])
        )
    
    async def _create_complex_plan(self, request: str, agents: List[str], context: Dict[str, Any]) -> List[PlanStep]:
        """Create a complex multi-step plan."""
        steps = []
        request_lower = request.lower()
        
        # Determine if this is a technical issue with order context
        if "order" in agents and "tech_support" in agents:
            # Order lookup first, then tech support
            order_step = self._create_step("order", "Retrieve order information", priority=1)
            tech_step = self._create_step("tech_support", "Provide technical assistance", priority=2)
            tech_step.depends_on = ["order"]
            steps.extend([order_step, tech_step])
            
            # Add solutions if customer seems frustrated
            if any(word in request_lower for word in ["help", "frustrated", "problem", "issue"]):
                solution_step = self._create_step("solutions", "Provide resolution options", priority=3)
                solution_step.depends_on = ["tech_support"]
                steps.append(solution_step)
        
        # Product comparison with alternatives
        elif "product" in agents and any(word in request_lower for word in ["other", "alternative", "different"]):
            product_step = self._create_step("product", "Compare product options", priority=1)
            alt_step = self._create_step("product", "Find alternatives", priority=2)
            alt_step.depends_on = ["product"]
            steps.extend([product_step, alt_step])
        
        # Default sequential execution
        else:
            for i, agent in enumerate(agents):
                step = self._create_step(agent, request, priority=i+1)
                if i > 0:
                    step.depends_on = [agents[i-1]]
                steps.append(step)
        
        return steps
    
    def _is_complex_request(self, request: str) -> bool:
        """Determine if a request is complex and needs conditional execution."""
        complexity_indicators = [
            "order" in request.lower() and any(word in request.lower() for word in ["not working", "broken", "help"]),
            len(request.split()) > 15,  # Long requests tend to be complex
            request.count("?") > 1,  # Multiple questions
            any(word in request.lower() for word in ["and", "also", "plus", "additionally"])
        ]
        
        return any(complexity_indicators)
    
    def _estimate_execution_time(self, steps: List[PlanStep]) -> int:
        """Estimate execution time in seconds."""
        base_time_per_step = 3  # Base time per agent
        tool_time = 2  # Additional time per tool
        
        total_time = 0
        for step in steps:
            step_time = base_time_per_step + (len(step.tools_required) * tool_time)
            total_time += step_time
        
        return min(total_time, 30)  # Cap at 30 seconds
    
    def _estimate_plan_confidence(self, steps: List[PlanStep], context: Dict[str, Any]) -> float:
        """Estimate confidence in the plan's success."""
        base_confidence = 0.7
        
        # Boost confidence based on context
        if context.get("orders_discussed") and any(s.agent_type == "order" for s in steps):
            base_confidence += 0.1
        
        if len(steps) == 1:
            base_confidence += 0.1  # Single agent plans are more reliable
        
        # Reduce confidence for very complex plans
        if len(steps) > 3:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.3), 0.95)
    
    def _has_circular_dependencies(self, steps: List[PlanStep]) -> bool:
        """Check for circular dependencies in the plan."""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_type: str) -> bool:
            if step_type in rec_stack:
                return True
            if step_type in visited:
                return False
            
            visited.add(step_type)
            rec_stack.add(step_type)
            
            # Find dependencies for this step
            for step in steps:
                if step.agent_type == step_type:
                    for dep in step.depends_on:
                        if has_cycle(dep):
                            return True
            
            rec_stack.remove(step_type)
            return False
        
        for step in steps:
            if step.agent_type not in visited:
                if has_cycle(step.agent_type):
                    return True
        
        return False
    
    def _generate_plan_id(self) -> str:
        """Generate a unique plan ID."""
        import uuid
        return f"plan-{str(uuid.uuid4())[:8]}"
    
    def _create_fallback_plan(self, request: str) -> ExecutionPlan:
        """Create a simple fallback plan when main planning fails."""
        plan = ExecutionPlan(request, "fallback-plan")
        plan.execution_mode = ExecutionMode.SEQUENTIAL
        plan.steps = [self._create_step("tech_support", request)]  # Default to tech support
        plan.estimated_time = 10
        plan.confidence = 0.5
        plan.status = "fallback"
        
        logger.warning("Created fallback plan due to planning error")
        return plan

# Global planner instance
planner = Planner()