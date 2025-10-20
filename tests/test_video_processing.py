import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.services.video_processing import process_and_insert_video_from_json

@pytest.fixture
def mock_session():
    return MagicMock()

@patch('app.services.video_processing.upsert_video')
def test_process_and_insert_video_from_json(mock_upsert_video, mock_session):
    video_json = {
        "id": "test_video_id",
        "snippet": {
            "publishedAt": "2025-10-18T22:00:00Z",
            "channelId": "test_channel_id",
            "title": "Test Video Title",
            "description": "Test video description.",
            "tags": ["tag1", "tag2"],
            "categoryId": "25",
            "channelTitle": "Test Channel Title",
            "defaultLanguage": "en"
        },
        "contentDetails": {
            "duration": "PT10M5S"
        },
        "statistics": {
            "viewCount": "100",
            "likeCount": "10",
            "commentCount": "5"
        }
    }

    process_and_insert_video_from_json(mock_session, video_json)

    expected_video_data = {
        "video_id": "test_video_id",
        "title": "Test Video Title",
        "description": "Test video description.",
        "channel_id": "test_channel_id",
        "channel_title": "Test Channel Title",
        "tags": ["tag1", "tag2"],
        "category_id": 25,
        "published_at": datetime(2025, 10, 18, 22, 0, 0, tzinfo=timezone.utc),
        "language": "en",
        "duration_iso": "PT10M5S",
        "view_count": 100,
        "like_count": 10,
        "comment_count": 5,
    }

    mock_upsert_video.assert_called_once_with(mock_session, expected_video_data)

def test_process_and_insert_video_from_empty_json(mock_session):
    """Tests that the function handles empty JSON gracefully."""
    with patch('app.services.video_processing.logger.warning') as mock_logger:
        process_and_insert_video_from_json(mock_session, None)
        mock_logger.assert_called_once_with("Received empty video JSON, skipping.")
