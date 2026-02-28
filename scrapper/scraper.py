from playwright.sync_api import sync_playwright

def scrape_upwork(keyword):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.upwork.com/search/jobs/?q={keyword}")
        page.wait_for_timeout(3000)

        cards = page.query_selector_all(".job-tile")
        for card in cards[:5]:
            jobs.append({
                "title": card.inner_text(),
                "platform": "upwork"
            })
        browser.close()
    return jobs
