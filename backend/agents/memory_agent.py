<<<<<<< HEAD
﻿"""
Memory Agent - Manages ChromaDB vector store for job and proposal history
"""
from typing import List, Dict, Optional
import chromadb
from backend.config import settings
import json
from datetime import datetime


class MemoryAgent:
    """Agent that manages vector memory for jobs and proposals"""
    
    def __init__(self):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Get or create collections
            self.jobs_collection = self.client.get_or_create_collection(
                name="jobs",
                metadata={"description": "Scraped job postings"}
            )
            
            self.proposals_collection = self.client.get_or_create_collection(
                name="proposals",
                metadata={"description": "Generated proposals"}
            )
            
            print("Success: ChromaDB initialized")
            
        except Exception as e:
            print(f"Warning: Error initializing ChromaDB: {e}")
            self.client = None
    
    def store_jobs(self, jobs: List[Dict]):
        """Store jobs in vector database"""
        if not self.client:
            print("Warning: ChromaDB not available")
            return
        
        try:
            for i, job in enumerate(jobs):
                # Create document text
                doc_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('tags', '')}"
                
                # Store in ChromaDB
                self.jobs_collection.add(
                    documents=[doc_text],
                    metadatas=[{
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'source': job.get('source', 'N/A'),
                        'source_url': job.get('source_url', ''),
                        'scraped_at': datetime.utcnow().isoformat()
                    }],
                    ids=[f"job_{datetime.utcnow().timestamp()}_{i}"]
                )
            
            print(f"Success: Stored {len(jobs)} jobs in vector memory")
            
        except Exception as e:
            print(f"Error: Error storing jobs: {e}")
    
    def store_proposals(self, proposals: List[Dict]):
        """Store proposals in vector database"""
        if not self.client:
            print("Warning: ChromaDB not available")
            return
        
        try:
            for i, proposal_data in enumerate(proposals):
                job = proposal_data.get('job', {})
                proposal = proposal_data.get('proposal', '')
                
                # Store in ChromaDB
                self.proposals_collection.add(
                    documents=[proposal],
                    metadatas=[{
                        'job_title': job.get('title', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'created_at': datetime.utcnow().isoformat()
                    }],
                    ids=[f"proposal_{datetime.utcnow().timestamp()}_{i}"]
                )
            
            print(f"Success: Stored {len(proposals)} proposals in vector memory")
            
        except Exception as e:
            print(f"Error: Error storing proposals: {e}")
    
    def search_similar_jobs(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar jobs in memory"""
        if not self.client:
            return []
        
        try:
            results = self.jobs_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Error: Error searching jobs: {e}")
            return []
    
    def search_similar_proposals(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar proposals in memory"""
        if not self.client:
            return []
        
        try:
            results = self.proposals_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Error: Error searching proposals: {e}")
            return []
    
    def run(self, state: dict) -> dict:
        """LangGraph node function"""
        print("\n🧠 Memory Agent: Storing in vector memory...")
        
        # Store jobs
        relevant_jobs = state.get('relevant_jobs', [])
        if relevant_jobs:
            self.store_jobs(relevant_jobs)
        
        # Store proposals
        proposals = state.get('proposals', [])
        if proposals:
            self.store_proposals(proposals)
        
        return state


if __name__ == "__main__":
    agent = MemoryAgent()
    
    # Test storing a job
    sample_jobs = [{
        'title': 'Python Developer',
        'description': 'Build FastAPI applications',
        'company': 'Tech Corp',
        'source': 'test',
        'tags': 'python,fastapi'
    }]
    agent.store_jobs(sample_jobs)
    
    # Test search
    results = agent.search_similar_jobs("Python FastAPI developer")
    print(f"\nSearch results: {results}")
=======
from backend.memory.vector_store import save_proposal, search_similar

def memory_agent(state):
    """
    Stores approved proposals and retrieves similar past wins
    """
    jobs = state.get("approved_jobs", [])

    for job in jobs:
        save_proposal(
            text=job["proposal"],
            metadata={
                "platform": job.get("platform"),
                "title": job.get("title"),
                "score": job.get("score")
            }
        )

    state["memory_saved"] = True
    return state
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
