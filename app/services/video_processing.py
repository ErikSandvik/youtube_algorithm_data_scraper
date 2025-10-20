import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.crud.video import upsert_video

logger = logging.getLogger(__name__)


def process_and_insert_video_from_json(session: Session, video_json_item: Dict[str, Any]):
    if not video_json_item:
        logger.warning("Received empty video JSON, skipping.")
        return

    snippet = video_json_item.get("snippet", {})
    content_details = video_json_item.get("contentDetails", {})
    statistics = video_json_item.get("statistics", {})

    video_data = {
        "video_id": video_json_item.get("id"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "tags": snippet.get("tags"),
        "category_id": int(snippet["categoryId"]) if snippet.get("categoryId") else None,
        "published_at": datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")) if snippet.get("publishedAt") else None,
        "language": snippet.get("defaultLanguage") or snippet.get("defaultAudioLanguage"),
        "duration_iso": content_details.get("duration"),
        "view_count": int(statistics["viewCount"]) if statistics.get("viewCount") else 0,
        "like_count": int(statistics["likeCount"]) if statistics.get("likeCount") else 0,
        "comment_count": int(statistics["commentCount"]) if statistics.get("commentCount") else 0,
    }

    try:
        upsert_video(session, video_data)
        logger.info(f"Successfully processed and saved video: {video_data['video_id']}")
    except Exception as e:
        logger.error(f"Failed to save video {video_data['video_id']}: {e}", exc_info=True)
        raise
