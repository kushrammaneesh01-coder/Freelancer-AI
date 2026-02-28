"""
We Work Remotely RSS Feed Scraper
Free RSS feed - no authentication needed
"""
import feedparser
from typing import List, Dict
from datetime import datetime
import time


class WeWorkRemotelyScraper:
    """Scraper for We Work Remotely jobs using RSS feed"""
    
    RSS_URLS = {
        'programming': 'https://weworkremotely.com/categories/remote-programming-jobs.rss',
        'devops': 'https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss',
        'design': 'https://weworkremotely.com/categories/remote-design-jobs.rss',
        'all': 'https://weworkremotely.com/categories/remote-full-time-jobs.rss'
    }
    
    def __init__(self):
        pass
    
    def scrape_jobs(self, category: str = 'all', limit: int = 50) -> List[Dict]:
        """
        Scrape jobs from We Work Remotely RSS feed
        
        Args:
            category: Job category (programming, devops, design, all)
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        try:
            rss_url = self.RSS_URLS.get(category, self.RSS_URLS['all'])
            print(f"Fetching jobs from We Work Remotely ({category})...")
            
            feed = feedparser.parse(rss_url)
            
            jobs = []
            for entry in feed.entries[:limit]:
                try:
                    parsed_job = self._parse_job(entry)
                    if parsed_job:
                        jobs.append(parsed_job)
                except Exception as e:
                    print(f"Error parsing job: {e}")
                    continue
            
            print(f"Scraped {len(jobs)} jobs from We Work Remotely")
            return jobs
            
        except Exception as e:
            print(f"Error scraping We Work Remotely: {e}")
            return self._get_sample_jobs()
    
    def _parse_job(self, entry) -> Dict:
        """Parse job data from RSS feed entry"""
        # Extract company and title from entry title
        title = entry.get('title', 'N/A')
        
        # Parse published date
        posted_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            posted_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        
        return {
            'title': title,
            'description': entry.get('summary', ''),
            'source': 'weworkremotely',
            'source_url': entry.get('link', ''),
            'company': entry.get('author', 'N/A'),
            'location': 'Remote',
            'job_type': 'remote',
            'tags': ','.join([tag.term for tag in entry.get('tags', [])]) if hasattr(entry, 'tags') else '',
            'posted_date': posted_date,
        }
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Return sample jobs if RSS feed fails"""
        return [
            {
                'title': 'Backend Engineer - Python/Django',
                'description': 'Remote backend engineer position for growing startup.',
                'source': 'weworkremotely',
                'source_url': 'https://weworkremotely.com/sample',
                'company': 'Remote Co',
                'location': 'Remote',
                'job_type': 'full-time',
                'tags': 'python,django,postgresql',
                'posted_date': datetime.utcnow(),
            }
        ]


if __name__ == "__main__":
    scraper = WeWorkRemotelyScraper()
    jobs = scraper.scrape_jobs(category='programming', limit=10)
    print(f"\nFound {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"- {job['title']}")
