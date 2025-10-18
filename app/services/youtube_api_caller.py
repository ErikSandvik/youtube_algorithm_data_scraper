import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

def get_video_id_from_url(video_url: str) -> str:
    return video_url[-11:]

def get_video_ids_from_urls(video_urls: list) -> list:
    return [get_video_id_from_url(url) for url in video_urls]

def fetch_video_data(video_id: str) -> dict:
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,contentDetails,statistics"
        f"&id={video_id}"
        f"&key={API_KEY}"
    )
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def call_youtube_api_multiple(video_ids: list) -> dict:
    ids_string = ",".join(video_ids)
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,contentDetails,statistics"
        f"&id={ids_string}"
        f"&key={API_KEY}"
    )
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_youtube_categories() -> dict:
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videoCategories"
        f"?part=snippet"
        f"&regionCode=US"
        f"&key={API_KEY}"
    )
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

if __name__ == "__main__":
    sample_video_url = "https://www.youtube.com/watch?v=lV_QcwbTlZU"
    video_id = get_video_id_from_url(sample_video_url)
    video_data = fetch_video_data(video_id)
    print(video_data)