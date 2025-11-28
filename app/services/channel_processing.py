import logging
from sqlalchemy.orm import Session
from app.crud.channel import get_channel_by_id, upsert_channel
from app.services.youtube_api_caller import fetch_channel_details

logger = logging.getLogger(__name__)


def process_and_insert_channels_from_videos(session: Session, video_data_list: list[dict]):
    channel_ids = set()
    for video_data in video_data_list:
        snippet = video_data.get('snippet', {})
        channel_id = snippet.get('channelId')
        if channel_id:
            channel_ids.add(channel_id)

    if not channel_ids:
        logger.warning("No channel IDs found in video data")
        return

    new_channel_ids = []
    for channel_id in channel_ids:
        if not get_channel_by_id(session, channel_id):
            new_channel_ids.append(channel_id)

    if not new_channel_ids:
        logger.info("All channels already exist in database. No new channels to fetch.")
        return

    logger.info(f"Found {len(new_channel_ids)} new channels to fetch from YouTube API")

    try:
        channel_response = fetch_channel_details(new_channel_ids)
        items = channel_response.get('items', [])

        if not items:
            logger.warning("No channel data returned from YouTube API")
            return

        logger.info(f"Fetched {len(items)} channels from YouTube API. Inserting into database...")

        inserted_count = 0
        for item in items:
            try:
                channel_id = item['id']
                snippet = item.get('snippet', {})
                topic_details = item.get('topicDetails', {})

                channel_data = {
                    'channel_id': channel_id,
                    'title': snippet.get('title', 'Unknown'),
                    'description': snippet.get('description'),
                    'country': snippet.get('country'),
                    'topic_categories': topic_details.get('topicCategories'),
                }

                upsert_channel(session, channel_data)
                inserted_count += 1

            except Exception as e:
                logger.error(f"Failed to insert channel {item.get('id')}: {e}")
                continue

        logger.info(f"Successfully inserted {inserted_count} channels into database")

    except Exception as e:
        logger.error(f"Error fetching channel details from YouTube API: {e}")
        raise

