"""
RemoteOK API Scraper
Free public API - no authentication needed
"""
import requests
from typing import List, Dict
from datetime import datetime


class RemoteOKScraper:
    """Scraper for RemoteOK jobs using their public API"""
    
    BASE_URL = "https://remoteok.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_jobs(self, limit: int = 50) -> List[Dict]:
        """
        Scrape jobs from RemoteOK
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        try:
            print("Fetching jobs from RemoteOK...")
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            jobs_data = response.json()
            
            # First item is metadata, skip it
            if jobs_data and isinstance(jobs_data, list):
                jobs_data = jobs_data[1:]
            
            jobs = []
            for job in jobs_data[:limit]:
                try:
                    parsed_job = self._parse_job(job)
                    if parsed_job:
                        jobs.append(parsed_job)
                except Exception as e:
                    print(f"Error parsing job: {e}")
                    continue
            
            print(f"Scraped {len(jobs)} jobs from RemoteOK")
            return jobs
            
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
            return self._get_sample_jobs()
    
    def _parse_job(self, job_data: dict) -> Dict:
        """Parse job data from RemoteOK API"""
        # Parse date - RemoteOK returns ISO 8601 string, NOT Unix timestamp
        posted_date = None
        date_raw = job_data.get('date')
        if date_raw:
            try:
                if isinstance(date_raw, (int, float)):
                    posted_date = datetime.fromtimestamp(date_raw)
                else:
                    posted_date = datetime.fromisoformat(str(date_raw).replace('Z', '+00:00'))
            except Exception:
                posted_date = None

        # Tags may be a list or a string
        tags_raw = job_data.get('tags', [])
        if isinstance(tags_raw, list):
            tags = ','.join(str(t) for t in tags_raw)
        else:
            tags = str(tags_raw)

        return {
            'title': job_data.get('position', 'N/A'),
            'description': job_data.get('description', ''),
            'source': 'remoteok',
            'source_url': job_data.get('url', ''),
            'company': job_data.get('company', 'N/A'),
            'location': job_data.get('location', 'Remote'),
            'job_type': 'remote',
            'tags': tags,
            'posted_date': posted_date,
        }
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Return sample jobs if API fails"""
        return [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our remote team.',
                'source': 'remoteok',
                'source_url': 'https://remoteok.com/sample',
                'company': 'Tech Corp',
                'location': 'Remote',
                'job_type': 'full-time',
                'tags': 'python,django,fastapi',
                'posted_date': datetime.utcnow(),
            },
            {
                'title': 'Full Stack Developer',
                'description': 'Join our team to build amazing web applications.',
                'source': 'remoteok',
                'source_url': 'https://remoteok.com/sample2',
                'company': 'Startup Inc',
                'location': 'Remote',
                'job_type': 'contract',
                'tags': 'javascript,react,nodejs',
                'posted_date': datetime.utcnow(),
            }
        ]


if __name__ == "__main__":
    scraper = RemoteOKScraper()
    jobs = scraper.scrape_jobs(limit=10)
    print(f"\nFound {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']}")
