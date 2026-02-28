from playwright.sync_api import sync_playwright

def scrape_freelancer(keyword: str):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://www.freelancer.com/jobs/{keyword.replace(' ', '-')}/"
        page.goto(url)
        page.wait_for_timeout(4000)

        cards = page.query_selector_all("div.JobSearchCard-item")

        for card in cards[:5]:
            title = card.query_selector("a.JobSearchCard-primary-heading-link")
            if title:
                jobs.append({
                    "platform": "freelancer",
                    "title": title.inner_text(),
                    "description": card.inner_text(),
                    "budget": None
                })

        browser.close()

    return jobs
