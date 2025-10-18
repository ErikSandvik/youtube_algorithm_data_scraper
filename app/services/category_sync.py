from __future__ import annotations
import logging
from sqlalchemy.orm import Session
from app.services.youtube_api_caller import fetch_youtube_categories

from app.models.category import Category

logger = logging.getLogger(__name__)


def sync_categories_from_youtube(session: Session):
    logger.info("Starting category population from YouTube API (adds missing only)...")
    try:
        api_response = fetch_youtube_categories()
        api_categories_raw = api_response.get('items', [])
    except Exception as e:
        logger.error(f"Could not fetch or parse categories from YouTube API: {e}")
        return

    new_categories_added = 0
    for item in api_categories_raw:
        cat_id = int(item['id'])
        # Check if the category already exists in the database
        if not session.get(Category, cat_id):
            cat_name = item.get('snippet', {}).get('title', 'Unknown')
            logger.info(f"New category found: ID={cat_id}, Name='{cat_name}'. Adding to DB.")
            session.add(Category(id=cat_id, name=cat_name))
            new_categories_added += 1

    if new_categories_added > 0:
        session.commit()
        logger.info(f"Category population complete. Added {new_categories_added} new categories.")
    else:
        logger.info("Category population complete. No new categories to add.")
