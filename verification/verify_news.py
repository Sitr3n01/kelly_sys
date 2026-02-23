from playwright.sync_api import sync_playwright

def verify_news():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8000/news/")
        # Wait for content to load
        page.wait_for_selector("h1")
        # Screenshot
        page.screenshot(path="verification/news_home.png", full_page=True)
        browser.close()

if __name__ == "__main__":
    verify_news()