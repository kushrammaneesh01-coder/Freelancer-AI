<<<<<<< HEAD
﻿"""
Pricing Agent - Suggests competitive pricing for jobs
"""
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.config import settings
import re


class PricingAgent:
    """Agent that suggests pricing for jobs"""
    
    def __init__(self):
        self.llm = None
        if settings.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI: {e}")
        
        self.pricing_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a freelance pricing expert. Analyze job postings and suggest competitive pricing.

Consider:
- Job complexity and requirements
- Required skills and experience level
- Project scope and timeline
- Market rates for similar work

Respond with ONLY a JSON object:
{{"min_price": 1000, "max_price": 3000, "recommended_price": 2000, "rationale": "brief explanation"}}

All prices in USD."""),
            ("user", """Job Title: {title}
Description: {description}
Tags/Skills: {tags}
Job Type: {job_type}

Suggest pricing for this job.""")
        ])
    
    def suggest_pricing(self, job: Dict) -> Dict:
        """
        Suggest pricing for a job
        
        Args:
            job: Job dictionary
            
        Returns:
            Dictionary with pricing suggestions
        """
        if not self.llm:
            print("Warning: OpenAI not configured, using basic pricing")
            return self._basic_pricing(job)
        
        try:
            chain = self.pricing_prompt | self.llm
            response = chain.invoke({
                'title': job.get('title', 'N/A'),
                'description': job.get('description', '')[:800],
                'tags': job.get('tags', 'N/A'),
                'job_type': job.get('job_type', 'N/A')
            })
            
            # Parse JSON response
            import json
            result = json.loads(response.content)
            print(f"Success: Suggested pricing: ${result.get('recommended_price', 0)}")
            return result
            
        except Exception as e:
            print(f"Error: Error suggesting pricing: {e}")
            return self._basic_pricing(job)
    
    def _basic_pricing(self, job: Dict) -> Dict:
        """Basic pricing logic without LLM"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        # Simple heuristic based on keywords
        base_price = 1500
        
        if 'senior' in title or 'lead' in title:
            base_price = 3000
        elif 'junior' in title or 'entry' in title:
            base_price = 800
        
        if 'full-stack' in title or 'fullstack' in title:
            base_price *= 1.3
        
        return {
            'min_price': int(base_price * 0.7),
            'max_price': int(base_price * 1.5),
            'recommended_price': int(base_price),
            'rationale': 'Based on job title and basic analysis'
        }
    
    def run(self, state: dict) -> dict:
        """LangGraph node function"""
        print("\n💰 Pricing Agent: Suggesting pricing...")
        proposals = state.get('proposals', [])
        
        for proposal_data in proposals:
            job = proposal_data['job']
            pricing = self.suggest_pricing(job)
            proposal_data['pricing'] = pricing
        
        state['proposals'] = proposals
        return state


if __name__ == "__main__":
    agent = PricingAgent()
    sample_job = {
        'title': 'Senior Python Developer',
        'description': 'Complex backend system with microservices architecture.',
        'tags': 'python,fastapi,docker,kubernetes',
        'job_type': 'contract'
    }
    pricing = agent.suggest_pricing(sample_job)
    print(f"\nPricing suggestion: {pricing}")
=======
def pricing_agent(state):
    for job in state["jobs"]:
        job["bid"] = int(job["budget"] * 0.9)
    return state
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
