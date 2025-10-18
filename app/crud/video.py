from __future__ import annotations
import logging
from typing import Iterable, Optional, Sequence, Union
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.video import Video

logger = logging.getLogger(__name__)


def get_video_by_id(session: Session, video_id: str) -> Optional[Video]:
    return session.get(Video, video_id)


def list_videos(session: Session, limit: int = 100, offset: int = 0) -> list[Video]:
    stmt = (
        select(Video)
        .order_by(Video.published_at.desc().nullslast())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(stmt))


def insert_video(session: Session, video: Union[Video, dict]) -> Video:
    obj = video if isinstance(video, Video) else Video(**video)
    session.add(obj)
    try:
        session.commit()
        session.refresh(obj)
        logger.info("Inserted video id=%s title=%s", obj.video_id, obj.title)
        return obj
    except IntegrityError as e:
        session.rollback()
        logger.error("Insert failed for video id=%s: %s", obj.video_id, e)
        raise


def upsert_video(session: Session, video: Union[Video, dict]) -> Video:
    data = {k: v for k, v in (video.__dict__ if isinstance(video, Video) else dict(video)).items() if k != '_sa_instance_state'}
    video_id = data.get("video_id")
    if not video_id:
        raise ValueError("video_id is required for upsert")

    existing = session.get(Video, video_id)
    if existing:
        for key, value in data.items():
            if key != "video_id":
                setattr(existing, key, value)
        session.commit()
        session.refresh(existing)
        logger.info("Updated video id=%s", existing.video_id)
        return existing

    return insert_video(session, data)
