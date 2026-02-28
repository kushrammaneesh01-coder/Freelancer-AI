<<<<<<< HEAD
﻿"""
Submission Agent - Prepares proposals for manual submission
"""
from typing import Dict, List


class SubmissionAgent:
    """Agent that prepares proposals for manual copy-paste submission"""
    
    def __init__(self):
        pass
    
    def prepare_for_submission(self, proposal_data: Dict) -> Dict:
        """
        Prepare a proposal for manual submission
        
        Args:
            proposal_data: Dictionary containing job, proposal, and pricing
            
        Returns:
            Formatted submission data
        """
        job = proposal_data.get('job', {})
        proposal = proposal_data.get('proposal', '')
        pricing = proposal_data.get('pricing', {})
        
        submission = {
            'job_title': job.get('title', 'N/A'),
            'company': job.get('company', 'N/A'),
            'job_url': job.get('source_url', ''),
            'proposal_text': proposal,
            'suggested_price': pricing.get('recommended_price', 0),
            'price_range': f"${pricing.get('min_price', 0)} - ${pricing.get('max_price', 0)}",
            'pricing_rationale': pricing.get('rationale', ''),
            'instructions': self._get_submission_instructions(job)
        }
        
        return submission
    
    def _get_submission_instructions(self, job: Dict) -> str:
        """Generate submission instructions"""
        source = job.get('source', 'unknown')
        url = job.get('source_url', '')
        
        instructions = f"""
MANUAL SUBMISSION INSTRUCTIONS:

1. Open the job posting: {url}
2. Copy the proposal text below
3. Paste it into the application form
4. Adjust pricing based on the suggestion
5. Review and submit manually

Warning:️ IMPORTANT: Always review and customize the proposal before submitting!
"""
        return instructions
    
    def prepare_batch(self, proposals: List[Dict]) -> List[Dict]:
        """Prepare multiple proposals for submission"""
        submissions = []
        for proposal_data in proposals:
            submission = self.prepare_for_submission(proposal_data)
            submissions.append(submission)
        
        print(f"Success: Prepared {len(submissions)} proposals for manual submission")
        return submissions
    
    def run(self, state: dict) -> dict:
        """LangGraph node function"""
        print("\n📤 Submission Agent: Preparing for manual submission...")
        proposals = state.get('proposals', [])
        submissions = self.prepare_batch(proposals)
        state['submissions'] = submissions
        state['ready_for_submission'] = len(submissions)
        return state


if __name__ == "__main__":
    agent = SubmissionAgent()
    
    sample_proposal = {
        'job': {
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'source_url': 'https://example.com/job/123'
        },
        'proposal': 'Sample proposal text...',
        'pricing': {
            'min_price': 1000,
            'max_price': 2000,
            'recommended_price': 1500,
            'rationale': 'Based on market rates'
        }
    }
    
    submission = agent.prepare_for_submission(sample_proposal)
    print(f"\nSubmission prepared:")
    print(f"Job: {submission['job_title']}")
    print(f"Price: ${submission['suggested_price']}")
=======
from backend.submission.safe_submit import safe_submit

def submission_agent(state):
    """
    SAFE submission agent (NO auto-send)
    """
    approved_jobs = state.get("approved_jobs", [])
    submissions = []

    for job in approved_jobs:
        submissions.append(safe_submit(job))

    return {
        "submissions": submissions
    }
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
