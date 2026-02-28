<<<<<<< HEAD
﻿"""
LangGraph Workflow - Multi-agent orchestration
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from backend.agents.job_scout import JobScoutAgent
from backend.agents.filter_agent import FilterAgent
from backend.agents.proposal_agent import ProposalAgent
from backend.agents.pricing_agent import PricingAgent
from backend.agents.memory_agent import MemoryAgent
from backend.agents.submission_agent import SubmissionAgent


class WorkflowState(TypedDict):
    """State shared across all agents"""
    jobs: List[Dict]
    total_jobs: int
    relevant_jobs: List[Dict]
    filtered_count: int
    proposals: List[Dict]
    proposal_count: int
    submissions: List[Dict]
    ready_for_submission: int
    error: str


class FreelanceWorkflow:
    """Multi-agent workflow for freelance automation"""
    
    def __init__(self):
        # Initialize agents
        self.job_scout = JobScoutAgent()
        self.filter_agent = FilterAgent()
        self.proposal_agent = ProposalAgent()
        self.pricing_agent = PricingAgent()
        self.memory_agent = MemoryAgent()
        self.submission_agent = SubmissionAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("scout", self.job_scout.run)
        workflow.add_node("filter", self.filter_agent.run)
        workflow.add_node("propose", self.proposal_agent.run)
        workflow.add_node("price", self.pricing_agent.run)
        workflow.add_node("memory", self.memory_agent.run)
        workflow.add_node("submit", self.submission_agent.run)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("scout")
        workflow.add_edge("scout", "filter")
        workflow.add_edge("filter", "propose")
        workflow.add_edge("propose", "price")
        workflow.add_edge("price", "memory")
        workflow.add_edge("memory", "submit")
        workflow.add_edge("submit", END)
        
        return workflow.compile()
    
    def run(self, initial_state: Dict = None) -> Dict:
        """
        Run the complete workflow
        
        Args:
            initial_state: Optional initial state
            
        Returns:
            Final workflow state
        """
        if initial_state is None:
            initial_state = {
                'jobs': [],
                'total_jobs': 0,
                'relevant_jobs': [],
                'filtered_count': 0,
                'proposals': [],
                'proposal_count': 0,
                'submissions': [],
                'ready_for_submission': 0,
                'error': ''
            }
        
        try:
            print("\n" + "="*60)
            print("🚀 Starting Freelance Automation Workflow")
            print("="*60)
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            print("\n" + "="*60)
            print("✅ Workflow Complete!")
            print("="*60)
            print(f"Total jobs found: {final_state.get('total_jobs', 0)}")
            print(f"Relevant jobs: {final_state.get('filtered_count', 0)}")
            print(f"Proposals generated: {final_state.get('proposal_count', 0)}")
            print(f"Ready for submission: {final_state.get('ready_for_submission', 0)}")
            print("="*60 + "\n")
            
            return final_state
            
        except Exception as e:
            print(f"\nError: Workflow error: {e}")
            initial_state['error'] = str(e)
            return initial_state


if __name__ == "__main__":
    # Test workflow
    workflow = FreelanceWorkflow()
    result = workflow.run()
    
    # Display sample submission
    if result.get('submissions'):
        print("\nSample Submission:")
        submission = result['submissions'][0]
        print(f"Job: {submission['job_title']}")
        print(f"Company: {submission['company']}")
        print(f"Suggested Price: ${submission['suggested_price']}")
        print(f"\nProposal:\n{submission['proposal_text'][:200]}...")
=======
from langgraph.graph import StateGraph
from agents.job_scout import job_scout
from agents.relevance_filter import relevance_filter
from agents.proposal_writer import proposal_writer
from agents.pricing_agent import pricing_agent
from agents.quality_checker import quality_checker

class State(dict): pass

graph = StateGraph(State)

graph.add_node("scout", job_scout)
graph.add_node("filter", relevance_filter)
graph.add_node("proposal", proposal_writer)
graph.add_node("pricing", pricing_agent)
graph.add_node("qc", quality_checker)

graph.set_entry_point("scout")

graph.add_edge("scout", "filter")
graph.add_edge("filter", "proposal")
graph.add_edge("proposal", "pricing")
graph.add_edge("pricing", "qc")

workflow = graph.compile()
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
