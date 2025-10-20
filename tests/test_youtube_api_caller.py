import pytest
from unittest.mock import patch, MagicMock
from app.services import youtube_api_caller

def test_get_video_id_from_url():
    assert youtube_api_caller.get_video_id_from_url("https://www.youtube.com/watch?v=lV_QcwbTlZU") == "lV_QcwbTlZU"

def test_get_video_ids_from_urls():
    urls = [
        "https://www.youtube.com/watch?v=lV_QcwbTlZU",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ]
    assert youtube_api_caller.get_video_ids_from_urls(urls) == ["lV_QcwbTlZU", "dQw4w9WgXcQ"]

@patch('app.services.youtube_api_caller.requests.get')
def test_fetch_video_data(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": "lV_QcwbTlZU"}]}
    mock_get.return_value = mock_response

    video_data = youtube_api_caller.fetch_video_data("lV_QcwbTlZU")

    mock_get.assert_called_once()
    assert video_data["items"][0]["id"] == "lV_QcwbTlZU"

@patch('app.services.youtube_api_caller.requests.get')
def test_call_youtube_api_multiple(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": "lV_QcwbTlZU"}, {"id": "dQw4w9WgXcQ"}]}
    mock_get.return_value = mock_response

    video_data = youtube_api_caller.call_youtube_api_multiple(["lV_QcwbTlZU", "dQw4w9WgXcQ"])

    mock_get.assert_called_once()
    assert len(video_data["items"]) == 2

@patch('app.services.youtube_api_caller.requests.get')
def test_fetch_youtube_categories(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": "1", "snippet": {"title": "Film & Animation"}}]}
    mock_get.return_value = mock_response

    categories = youtube_api_caller.fetch_youtube_categories()

    mock_get.assert_called_once()
    assert categories["items"][0]["id"] == "1"

@patch('app.services.youtube_api_caller.call_youtube_api_multiple')
def test_fetch_video_data_from_urls(mock_call_multiple):
    recommendations = [
        {"url": "https://www.youtube.com/watch?v=lV_QcwbTlZU"},
        {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        {"url": "https://www.youtube.com/watch?v=lV_QcwbTlZU"},  # Duplicate
    ]
    expected_video_ids = sorted(["lV_QcwbTlZU", "dQw4w9WgXcQ"])

    mock_call_multiple.return_value = {"items": []}

    youtube_api_caller.fetch_video_data_from_urls(recommendations)

    mock_call_multiple.assert_called_once_with(expected_video_ids)

@patch('app.services.youtube_api_caller.requests.get')
def test_call_youtube_api_multiple_with_chunking(mock_get):
    video_ids = [f"video_id_{i}" for i in range(51)]

    mock_response_1 = MagicMock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = {"items": [{"id": f"video_id_{i}"} for i in range(50)]}

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = {"items": [{"id": "video_id_50"}]}

    mock_get.side_effect = [mock_response_1, mock_response_2]

    video_data = youtube_api_caller.call_youtube_api_multiple(video_ids)

    assert mock_get.call_count == 2
    assert len(video_data["items"]) == 51
