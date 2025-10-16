from playwright.sync_api import sync_playwright
import logging
import csv, time, datetime
import random

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
        logging.info("Navigated to YouTube Shorts")
        page.wait_for_selector("ytd-reel-video-renderer", timeout=15000)
        time.sleep(5)
    except Exception as e:
        logging.error(f"Error clicking YouTube Shorts: {e}")

def click_home(page):
    try:
        logging.info("Clicking on Home")
        page.locator("a:has-text('Home')").click()
        page.wait_for_selector("a.yt-lockup-metadata-view-model__title", timeout=15000)
        logging.info("Navigated to Home")
    except Exception as e:
        logging.error(f"Error clicking Home: {e}")

def get_visible_video_indices(videos):
    count = videos.count()
    return [i for i in range(count) if videos.nth(i).is_visible()]

def click_video_by_index(page, videos, idx):
    videos.nth(idx).scroll_into_view_if_needed()
    videos.nth(idx).click()

def wait_for_video_player(page, url_before):
    try:
        page.wait_for_selector("video.html5-main-video", timeout=15000)
        url_after = page.url
        logging.info(f"URL after click: {url_after}")
        if url_after == url_before:
            logging.warning("URL did not change after click. Possible navigation issue.")
        logging.info("Random video selected and opened.")
    except Exception as e:
        logging.error(f"Video player did not appear after click: {e}")
        html = page.content()
        logging.debug(f"Page HTML after failed navigation:\n{html[:2000]}")

def select_random_video(page):
    try:
        logging.info("Waiting for video cards to load on the page...")
        videos = page.locator("a.yt-lockup-metadata-view-model__title")
        count = videos.count()
        logging.info(f"Found {count} video cards on this page.")
        if count == 0:
            logging.error("No video cards found on the page.")
            return
        visible_indices = get_visible_video_indices(videos)
        if not visible_indices:
            logging.error("No visible video cards found on the page.")
            return
        idx = random.choice(visible_indices)
        logging.info(f"Clicking visible video card #{idx + 1}.")
        url_before = page.url
        logging.info(f"URL before click: {url_before}")
        click_video_by_index(page, videos, idx)
        wait_for_video_player(page, url_before)
    except Exception as e:
        logging.error(f"Error selecting random video: {e}")

def run_random_video_selection(page, iterations: int = 5):
    for i in range(iterations):
        logging.info(f"Selecting random video iteration {i + 1} of {iterations}")
        select_random_video(page)
        time.sleep(5)

def main(headless: bool = True):
    initialize_logging()
    page, browser, context = launch_site(headless)
    accept_cookies(page)
    click_youtube_shorts(page)
    click_home(page)
    run_random_video_selection(page, iterations=5)
    logging.info("Waiting for 10 seconds before closing the browser...")
    time.sleep(10)
    browser.close()


if __name__ == "__main__":
    main(headless=False)
