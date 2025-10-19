import pytest
from unittest.mock import MagicMock, patch
from app.services import yt_agent

@pytest.fixture
def mock_playwright():
    with patch('app.services.yt_agent.sync_playwright') as mock_sync_playwright:
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # Mock the context manager entry
        mock_sync_playwright.return_value.__enter__.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        yield {
            "page": mock_page,
            "browser": mock_browser,
            "context": mock_context,
            "playwright": mock_p
        }

def test_launch_site(mock_playwright):
    page, browser, context = yt_agent.launch_site(mock_playwright["playwright"], headless=True)

    assert page is not None
    assert browser is not None
    assert context is not None

    mock_playwright["playwright"].chromium.launch.assert_called_once_with(headless=True)
    mock_playwright["page"].goto.assert_called_once_with("https://www.youtube.com")

def test_accept_cookies(mock_playwright):
    mock_page = mock_playwright["page"]
    yt_agent.accept_cookies(mock_page)
    mock_page.locator("button:has-text('Accept All')").click.assert_called_once()

def test_click_youtube_shorts(mock_playwright):
    mock_page = mock_playwright["page"]
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator
    yt_agent.click_youtube_shorts(mock_page)
    mock_locator.first.click.assert_called_once()

def test_click_home(mock_playwright):
    mock_page = mock_playwright["page"]
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator
    yt_agent.click_home(mock_page)
    mock_locator.first.click.assert_called_once()

def test_select_random_video(mock_playwright):
    mock_page = mock_playwright["page"]
    mock_videos_locator = MagicMock()
    mock_page.locator.return_value = mock_videos_locator

    mock_videos_locator.count.return_value = 3
    mock_videos_locator.nth.return_value.is_visible.return_value = True
    mock_videos_locator.evaluate_all.return_value = ['/watch?v=1', '/watch?v=2', '/watch?v=3']


    with patch('app.services.yt_agent.random.choice', return_value=1) as mock_random_choice:
        yt_agent.select_random_video_and_get_recommendations(mock_page)

        mock_page.locator.assert_called_with("a.yt-lockup-metadata-view-model__title")

        mock_random_choice.assert_called_once()

        mock_videos_locator.nth.assert_any_call(1)
        mock_videos_locator.nth.return_value.click.assert_called_once()
