"""
Adzuna API Scraper
Free tier available - requires API key from https://developer.adzuna.com/
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime


class AdzunaScraper:
    """Scraper for Adzuna jobs using their API"""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        """
        Initialize Adzuna scraper
        
        Args:
            app_id: Adzuna App ID (get from https://developer.adzuna.com/)
            app_key: Adzuna App Key
        """
        self.app_id = app_id
        self.app_key = app_key
        self.session = requests.Session()
    
    def scrape_jobs(self, country: str = 'us', query: str = 'python developer', 
                   limit: int = 50) -> List[Dict]:
        """
        Scrape jobs from Adzuna API
        
        Args:
            country: Country code (us, gb, ca, etc.)
            query: Search query
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        if not self.app_id or not self.app_key:
            print("Adzuna API credentials not provided, using sample data")
            return self._get_sample_jobs()
        
        try:
            print(f"Fetching jobs from Adzuna ({country})...")
            
            url = f"{self.BASE_URL}/{country}/search/1"
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': min(limit, 50),
                'what': query,
                'content-type': 'application/json'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            jobs = []
            for job in results:
                try:
                    parsed_job = self._parse_job(job)
                    if parsed_job:
                        jobs.append(parsed_job)
                except Exception as e:
                    print(f"Error parsing job: {e}")
                    continue
            
            print(f"Scraped {len(jobs)} jobs from Adzuna")
            return jobs
            
        except Exception as e:
            print(f"Error scraping Adzuna: {e}")
            return self._get_sample_jobs()
    
    def _parse_job(self, job_data: dict) -> Dict:
        """Parse job data from Adzuna API"""
        # Parse created date
        posted_date = None
        if job_data.get('created'):
            try:
                posted_date = datetime.fromisoformat(job_data['created'].replace('Z', '+00:00'))
            except:
                pass
        
        return {
            'title': job_data.get('title', 'N/A'),
            'description': job_data.get('description', ''),
            'source': 'adzuna',
            'source_url': job_data.get('redirect_url', ''),
            'company': job_data.get('company', {}).get('display_name', 'N/A'),
            'location': job_data.get('location', {}).get('display_name', 'N/A'),
            'job_type': job_data.get('contract_type', 'N/A'),
            'tags': job_data.get('category', {}).get('label', ''),
            'posted_date': posted_date,
        }
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Return sample jobs if API fails or credentials missing"""
        return [
            {
                'title': 'Python Software Engineer',
                'description': 'Looking for a skilled Python developer with FastAPI experience.',
                'source': 'adzuna',
                'source_url': 'https://adzuna.com/sample',
                'company': 'Tech Solutions',
                'location': 'New York, NY',
                'job_type': 'permanent',
                'tags': 'IT Jobs',
                'posted_date': datetime.utcnow(),
            },
            {
                'title': 'Full Stack Developer',
                'description': 'Join our team to build cutting-edge web applications.',
                'source': 'adzuna',
                'source_url': 'https://adzuna.com/sample2',
                'company': 'Digital Agency',
                'location': 'San Francisco, CA',
                'job_type': 'contract',
                'tags': 'IT Jobs',
                'posted_date': datetime.utcnow(),
            }
        ]


if __name__ == "__main__":
    # Test with sample data (no API key)
    scraper = AdzunaScraper()
    jobs = scraper.scrape_jobs(query='python developer', limit=10)
    print(f"\nFound {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']}")
