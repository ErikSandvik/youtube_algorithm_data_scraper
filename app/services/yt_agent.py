from playwright.sync_api import sync_playwright
import logging
import csv, time, datetime
import random
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)

def launch_site(p, headless: bool = True):
    try:
        logging.info(f"Starting Playwright with headless={headless}")
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

def click_youtube_shorts(page):
    try:
        logging.info("Clicking on YouTube Shorts")
        page.locator("a:has-text('Shorts')").first.click()
        logging.info("Navigated to YouTube Shorts")
        page.wait_for_selector("ytd-reel-video-renderer", timeout=15000)
        time.sleep(5)
    except Exception as e:
        logging.error(f"Error clicking YouTube Shorts: {e}")

def click_home(page):
    try:
        logging.info("Clicking on Home")
        page.locator("a:has-text('Home')").first.click()
        page.wait_for_selector("a.yt-lockup-metadata-view-model__title", timeout=15000)
        logging.info("Navigated to Home")
    except Exception as e:
        logging.error(f"Error clicking Home: {e}")

def get_visible_video_indices(videos):
    count = videos.count()
    return [i for i in range(count) if videos.nth(i).is_visible()]

def click_video_by_index(videos, index):
    videos.nth(index).scroll_into_view_if_needed()
    videos.nth(index).click()

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

def select_random_video_and_get_recommendations(page):
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

        recommended_video_urls = get_recommended_video_urls(videos)
        visible_recommended_urls = [recommended_video_urls[i] for i in visible_indices]

        select_random_video(page, videos, visible_indices)

        return visible_recommended_urls
    except Exception as e:
        logging.error(f"Error selecting random video: {e}")

def select_random_video(page, videos, possible_indices):
    chosen_video_index = random.choice(possible_indices)
    logging.info(f"Clicking visible video card #{chosen_video_index + 1}.")
    url_before = page.url
    logging.info(f"URL before click: {url_before}")

    click_video_by_index(videos, chosen_video_index)
    wait_for_video_player(page, url_before)

def get_recommended_video_urls(videos_locator):
    try:
        hrefs = videos_locator.evaluate_all("els => els.map(e => e.getAttribute('href'))")
        full_urls = []
        for href in hrefs:
            if href:
                full_url = urljoin("https://www.youtube.com", href)
                full_urls.append(full_url)
        return full_urls
    except Exception as e:
        logging.error(f"Error getting video URLs: {e}")
        return []

def run_random_video_selection(page, iterations: int = 5):
    recommendations = []
    for i in range(iterations):
        logging.info(f"Selecting random video iteration {i + 1} of {iterations}")
        recommended_links = select_random_video_and_get_recommendations(page)
        if recommended_links:
            recommendations.extend(recommended_links)
        time.sleep(5)
    return recommendations

def run_yt_agent(headless: bool = True, iterations: int = 10):
    with sync_playwright() as p:
        page, browser, context = launch_site(p, headless)
        if not page:
            logging.error("Failed to launch site, aborting agent run.")
            return []

        try:
            accept_cookies(page)
            click_youtube_shorts(page)
            click_home(page)
            recommendations = run_random_video_selection(page, iterations)

            logging.info("Waiting for 10 seconds before closing the browser...")
            time.sleep(10)

            return recommendations
        except Exception as e:
            logging.error(f"An error occurred during agent execution: {e}", exc_info=True)
            return []
        finally:
            if browser:
                browser.close()

if __name__ == "__main__":
    recommendations = run_yt_agent(headless=False)
