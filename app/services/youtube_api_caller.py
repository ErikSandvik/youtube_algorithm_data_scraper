import os
import requests
from dotenv import load_dotenv

from app.services.exceptions import QuotaExceededError

load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

def get_video_id_from_url(video_url: str) -> str:
    return video_url[-11:]

def get_video_ids_from_urls(video_urls: list) -> list:
    return [get_video_id_from_url(url) for url in video_urls]

def _handle_api_response(response: requests.Response):
    if response.status_code == 403:
        error_details = response.json()
        if 'error' in error_details and 'errors' in error_details['error']:
            for error in error_details['error']['errors']:
                if error.get('reason') == 'quotaExceeded':
                    raise QuotaExceededError("YouTube API quota exceeded.")
    response.raise_for_status()

def fetch_video_data(video_id: str) -> dict:
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,contentDetails,statistics"
        f"&id={video_id}"
        f"&key={API_KEY}"
    )
    response = requests.get(api_url)
    _handle_api_response(response)
    return response.json()

def call_youtube_api_multiple(video_ids: list) -> dict:
    all_items = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        ids_string = ",".join(chunk)
        api_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,contentDetails,statistics"
            f"&id={ids_string}"
            f"&key={API_KEY}"
        )
        response = requests.get(api_url)
        _handle_api_response(response)
        data = response.json()
        all_items.extend(data.get('items', []))

    return {'items': all_items}

def fetch_youtube_categories() -> dict:
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videoCategories"
        f"?part=snippet"
        f"&regionCode=US"
        f"&key={API_KEY}"
    )
    response = requests.get(api_url)
    _handle_api_response(response)
    return response.json()

def fetch_video_data_from_urls(video_urls: list) -> dict:
    video_ids = get_video_ids_from_urls(video_urls)
    return call_youtube_api_multiple(video_ids)

if __name__ == "__main__":
    sample_video_url = "https://www.youtube.com/watch?v=lV_QcwbTlZU"
    video_id = get_video_id_from_url(sample_video_url)
    video_data = fetch_video_data(video_id)
    print(video_data)