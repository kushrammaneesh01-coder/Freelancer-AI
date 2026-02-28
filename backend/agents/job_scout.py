"""
Job Scout Agent - Orchestrates job scraping from multiple sources
"""
from typing import List, Dict
from scraper.remoteok import RemoteOKScraper
from scraper.weworkremotely import WeWorkRemotelyScraper
from scraper.adzuna import AdzunaScraper
from backend.config import settings


class JobScoutAgent:
    """Agent that scouts jobs from multiple free sources"""
    
    def __init__(self):
        self.remoteok = RemoteOKScraper()
        self.weworkremotely = WeWorkRemotelyScraper()
        self.adzuna = AdzunaScraper(
            app_id=settings.ADZUNA_APP_ID,
            app_key=settings.ADZUNA_APP_KEY
        )
    
    def scout_jobs(self, sources: List[str] = None, limit_per_source: int = 20) -> List[Dict]:
        """
        Scout jobs from multiple sources
        
        Args:
            sources: List of sources to scrape (remoteok, weworkremotely, adzuna)
                    If None, scrapes from all sources
            limit_per_source: Maximum jobs to fetch from each source
            
        Returns:
            Combined list of jobs from all sources
        """
        if sources is None:
            sources = ['remoteok', 'weworkremotely', 'adzuna']
        
        all_jobs = []
        
        # RemoteOK
        if 'remoteok' in sources:
            try:
                jobs = self.remoteok.scrape_jobs(limit=limit_per_source)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping RemoteOK: {e}")
        
        # We Work Remotely
        if 'weworkremotely' in sources:
            try:
                jobs = self.weworkremotely.scrape_jobs(
                    category='programming',
                    limit=limit_per_source
                )
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping We Work Remotely: {e}")
        
        # Adzuna
        if 'adzuna' in sources:
            try:
                jobs = self.adzuna.scrape_jobs(
                    query='python developer',
                    limit=limit_per_source
                )
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping Adzuna: {e}")
        
        print(f"\nSuccess: Total jobs scouted: {len(all_jobs)}")
        return all_jobs
    
    def run(self, state: dict) -> dict:
        """LangGraph node function"""
        print("\n🔍 Job Scout Agent: Scouting jobs...")
        jobs = self.scout_jobs()
        state['jobs'] = jobs
        state['total_jobs'] = len(jobs)
        return state


if __name__ == "__main__":
    agent = JobScoutAgent()
    jobs = agent.scout_jobs(limit_per_source=5)
    print(f"\nSample jobs:")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']} ({job['source']})")
