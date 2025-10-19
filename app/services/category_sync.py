from __future__ import annotations
import logging
from sqlalchemy.orm import Session
from app.services.youtube_api_caller import fetch_youtube_categories

from app.models.category import Category
from app.crud.category import get_category_by_name

logger = logging.getLogger(__name__)


def sync_categories_from_youtube(session: Session):
    logger.info("Starting category population from YouTube API (adds missing only)...")
    try:
        api_response = fetch_youtube_categories()
        api_categories_raw = api_response.get('items', [])
    except Exception as e:
        logger.error(f"Could not fetch or parse categories from YouTube API: {e}")
        return

    processed_names = set()

    for cat_item in api_categories_raw:
        cat_id = int(cat_item['id'])
        cat_name = cat_item['snippet']['title']

        if cat_name in processed_names:
            continue

        existing_category = get_category_by_name(session, cat_name)

        if existing_category:
            if existing_category.id != cat_id:
                logger.warning(
                    f"Category '{cat_name}' already exists with ID {existing_category.id}, "
                    f"but API returned new ID {cat_id}. Skipping update to avoid conflicts."
                )
        else:
            new_category = Category(id=cat_id, name=cat_name)
            session.add(new_category)
            processed_names.add(cat_name)
            logger.info(f"New category found: ID={cat_id}, Name='{cat_name}'. Adding to DB.")

    try:
        session.commit()
        logger.info("--- Category Sync Finished ---")
    except Exception as e:
        logger.error(f"An error occurred during category sync commit: {e}", exc_info=True)
        session.rollback()
        raise
