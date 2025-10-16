from playwright.sync_api import sync_playwright
import logging
import csv, time, datetime

def launch_site(headless: bool = True):
    try:
        logging.info(f"Starting Playwright with headless={headless}")
        p = sync_playwright().start()
        logging.info("Launching Chromium browser")
        browser = p.chromium.launch(headless=headless)
        logging.info("Creating new browser context")
        context = browser.new_context()
        logging.info("Opening new page")
        page = context.new_page()
        logging.info("Navigating to https://www.youtube.com")
        page.goto("https://www.youtube.com")
        logging.info("Waiting for network to be idle")
        page.wait_for_load_state("networkidle")
        logging.info("Site launched and ready")
        return page, browser, context
    except Exception as e:
        logging.error(f"Error in launch_site: {e}")
        return None, None, None

def accept_cookies(page):
    try:
        page.locator("button:has-text('Accept All')").click()
        logging.info("Accepted cookies")
    except Exception as e:
        logging.warning(f"No cookie consent button found or error occurred: {e}")


def initialize_logging():
    logging.basicConfig(level=logging.INFO)

def click_youtube_shorts(page):
    try:
        logging.info("Clicking on YouTube Shorts")
        page.locator("a:has-text('Shorts')").click()
        page.wait_for_load_state("networkidle")
        logging.info("Navigated to YouTube Shorts")
    except Exception as e:
        logging.error(f"Error clicking YouTube Shorts: {e}")

def click_home(page):
    try:
        logging.info("Clicking on Home")
        page.locator("a:has-text('Home')").click()
        page.wait_for_load_state("networkidle")
        logging.info("Navigated to Home")
    except Exception as e:
        logging.error(f"Error clicking Home: {e}")

def main(headless: bool = True):
    initialize_logging()
    page, browser, context = launch_site(headless)
    accept_cookies(page)
    click_youtube_shorts(page)
    click_home(page)


if __name__ == "__main__":
    main(headless=False)
