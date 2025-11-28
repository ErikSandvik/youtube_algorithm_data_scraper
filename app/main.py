import logging
import time
import uuid

from app.crud.rec_event import insert_rec_events
from app.services.category_sync import sync_categories_from_youtube
from app.services.video_processing import process_and_insert_video_from_json
from app.services.channel_processing import process_and_insert_channels_from_videos
from app.services.youtube_api_caller import fetch_video_data_from_urls, get_video_id_from_url
from app.services.yt_agent import run_yt_agent
from app.db import get_session
from app.services.exceptions import QuotaExceededError

logging.basicConfig(level=logging.INFO)


def is_video_data_valid(video_data: dict) -> bool:
    if not video_data or not isinstance(video_data, dict):
        return False

    required_keys = ['id', 'snippet', 'statistics', 'contentDetails']
    if not all(key in video_data for key in required_keys):
        logging.warning(f"Validation failed: Missing one of the required keys: {required_keys} in video data.")
        return False

    if 'title' not in video_data.get('snippet', {}):
        logging.warning("Validation failed: Missing 'title' in snippet.")
        return False
    if 'channelId' not in video_data.get('snippet', {}):
        logging.warning("Validation failed: Missing 'channelId' in snippet.")
        return False

    return True


def gather_recommendations_insert_into_db(session, videos_to_click: int = 3, headless: bool = True):
    logging.info(f"Starting new data gathering cycle with {videos_to_click} videos to click.")
    run_id = uuid.uuid4()

    recommendations = run_yt_agent(headless, iterations=videos_to_click)
    if not recommendations:
        logging.warning("No recommendations were gathered from the agent. Skipping this cycle.")
        return

    logging.info(f"Successfully gathered {len(recommendations)} video recommendations. Fetching data...")
    json_response = fetch_video_data_from_urls(recommendations)
    if not json_response or 'items' not in json_response:
        logging.warning("Could not fetch video data from YouTube API or data is malformed. Skipping this cycle.")
        return

    video_data_list = json_response['items']
    logging.info(f"Received {len(video_data_list)} video data items from API.")

    valid_video_data = [data for data in video_data_list if is_video_data_valid(data)]
    if not valid_video_data:
        logging.warning("No valid video data found after validation. Skipping insertion.")
        return
    
    logging.info("Processing and inserting channels for videos...")
    try:
        process_and_insert_channels_from_videos(session, valid_video_data)
    except Exception as e:
        logging.error(f"Failed to process channels: {e}")


    logging.info(f"Found {len(valid_video_data)} valid videos to insert. Processing and inserting...")
    for video_data in valid_video_data:
        try:
            process_and_insert_video_from_json(session, video_data)
        except Exception as e:
            logging.error(f"Failed to process and insert video {video_data.get('id')}: {e}")

    logging.info("Creating recommendation events...")
    rec_events = [
        {
            "run_id": run_id,
            "iteration": rec["iteration"],
            "source_video_id": rec["source_video_id"],
            "video_id": get_video_id_from_url(rec["url"]),
            "position": rec["position"],
        }
        for rec in recommendations
    ]

    try:
        insert_rec_events(session, rec_events)
    except Exception as e:
        logging.error(f"Failed to insert recommendation events: {e}")

    logging.info(f"Completed processing and inserting {len(rec_events)} recommendation events into the database.")


def main_loop(initial_wait_seconds: int = 5, error_wait_seconds: int = 60, quota_wait_hours: int = 6, headless: bool = True):
    logging.info("--- Starting Main Application Loop ---")
    time.sleep(initial_wait_seconds)
    quota_wait_seconds = quota_wait_hours * 3600

    while True:
        try:
            with get_session() as session:
                gather_recommendations_insert_into_db(session, videos_to_click=30, headless=headless)
            logging.info(f"Cycle finished. Waiting for {error_wait_seconds} seconds before next run.")
            time.sleep(error_wait_seconds)
        except QuotaExceededError as e:
            logging.error(f"YouTube API quota exceeded: {e}")
            logging.info(f"Application will sleep for {quota_wait_hours} hours before retrying.")
            time.sleep(quota_wait_seconds)
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            logging.info(f"Restarting loop after a {error_wait_seconds} second delay...")
            time.sleep(error_wait_seconds)


if __name__ == "__main__":
    with get_session() as session:
        sync_categories_from_youtube(session)
    main_loop(headless=True)
