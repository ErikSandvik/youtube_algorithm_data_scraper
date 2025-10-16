import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

def get_video_id_from_url(video_url: str) -> str:
    return video_url[-11:]

