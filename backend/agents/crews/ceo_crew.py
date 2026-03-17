"""
CEO Crew for AI Software Factory.

This crew handles strategic decision making, project oversight,
and executive-level coordination.
"""

from crewai import Crew, Agent, Task
from typing import Dict, List, Optional, Any

from backend.core.logging import get_logger
from backend.agents.base_agent import BaseAgent

logger = get_logger(__name__)


class CEOCrew(BaseAgent):
    """
    CEO Crew for strategic oversight.
    
    Provides executive decision making and project coordination
    capabilities.
    """
    
    def __init__(self):
        """Initialize the CEO crew."""
        super().__init__(name="CEO Crew")
        self._logger = get_logger(__name__)
    
    def create_crew(self) -> Crew:
        """Create the CEO crew with agents."""
        # CEO Agent
        ceo = Agent(
            role="Chief Executive Officer",
            goal="Make strategic decisions and oversee project success",
            backstory="""You are an experienced CEO with deep knowledge of software
            engineering, product management, and business strategy. You make
            high-level decisions about project direction and resource allocation.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Product Manager Agent
        pm = Agent(
            role="Product Manager",
            goal="Define product requirements and prioritize features",
            backstory="""You are a skilled product manager who translates business
            needs into technical requirements. You prioritize features and ensure
            the product meets user needs.""",
            verbose=True
        )
        
        # Technical Lead Agent
        tech_lead = Agent(
            role="Technical Lead",
            goal="Provide technical direction and architecture decisions",
            backstory="""You are a senior technical lead with expertise in modern
            software architecture. You make key technical decisions and ensure
            technical excellence.""",
            verbose=True
        )
        
        # Create crew
        crew = Crew(
            agents=[ceo, pm, tech_lead],
            tasks=[],
            verbose=True
        )
        
        return crew
    
    async def make_strategic_decision(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a strategic decision based on context.
        
        Args:
            context: Decision context including project state, options, constraints
            
        Returns:
            Decision with rationale
        """
        crew = self.create_crew()
        
        decision_task = Task(
            description=f"""Based on the following context, make a strategic decision:
            
            Project State: {context.get('project_state', 'Unknown')}
            Options: {context.get('options', [])}
            Constraints: {context.get('constraints', [])}
            
            Provide:
            1. The decision
            2. Rationale
            3. Risk assessment
            4. Next steps
            """,
            expected_output="A strategic decision with detailed rationale",
            agent=crew.agents[0]  # CEO agent
        )
        
        crew.tasks = [decision_task]
        result = crew.kickoff()
        
        return {
            "decision": result,
            "crew": "CEO Crew",
            "context": context
        }
    
    async def review_project_status(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review project status and provide executive summary.
        
        Args:
            project_data: Project metrics and status
            
        Returns:
            Executive summary with recommendations
        """
        crew = self.create_crew()
        
        review_task = Task(
            description=f"""Review the following project status and provide an executive summary:
            
            Project: {project_data.get('name', 'Unknown')}
            Status: {project_data.get('status', 'Unknown')}
            Progress: {project_data.get('progress', 0)}%
            Issues: {project_data.get('issues', [])}
            
            Provide:
            1. Executive summary
            2. Key concerns
            3. Recommendations
            4. Resource needs
            """,
            expected_output="Executive project review",
            agent=crew.agents[0]
        )
        
        crew.tasks = [review_task]
        result = crew.kickoff()
        
        return {
            "review": result,
            "crew": "CEO Crew",
            "project": project_data.get('name')
        }
