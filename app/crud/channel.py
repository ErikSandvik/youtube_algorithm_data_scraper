from __future__ import annotations
import logging
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.channel import Channel

logger = logging.getLogger(__name__)


def get_channel_by_id(session: Session, channel_id: str) -> Optional[Channel]:
    """Get a channel by its channel_id."""
    return session.get(Channel, channel_id)


def upsert_channel(session: Session, channel_data: dict) -> Channel:
    """
    Insert or update a channel in the database.
    If the channel already exists, it will be updated with new data.
    """
    channel_id = channel_data.get("channel_id")
    if not channel_id:
        raise ValueError("channel_id is required for upsert")

    existing = session.get(Channel, channel_id)
    if existing:
        # Update existing channel with new data
        for key, value in channel_data.items():
            if key != "channel_id":
                setattr(existing, key, value)
        session.commit()
        session.refresh(existing)
        logger.info(f"Updated channel id={existing.channel_id}")
        return existing

    # Insert new channel
    new_channel = Channel(**channel_data)
    session.add(new_channel)
    try:
        session.commit()
        session.refresh(new_channel)
        logger.info(f"Inserted new channel id={new_channel.channel_id} title={new_channel.title}")
        return new_channel
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Insert failed for channel id={channel_id}: {e}")
        raise

