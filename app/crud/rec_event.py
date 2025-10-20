from __future__ import annotations
import logging
from typing import Iterable, Union
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.rec_event import RecEvent

logger = logging.getLogger(__name__)


def insert_rec_event(session: Session, event: Union[RecEvent, dict]) -> RecEvent:
    obj = event if isinstance(event, RecEvent) else RecEvent(**event)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    logger.info(
        "Inserted recommendation event for video_id=%s with iteration=%s",
        obj.video_id,
        obj.iteration,
    )
    return obj


def insert_rec_events(
    session: Session, events: Iterable[Union[RecEvent, dict]]
) -> list[RecEvent]:
    objects = [
        event if isinstance(event, RecEvent) else RecEvent(**event) for event in events
    ]
    session.bulk_save_objects(objects, return_defaults=True)
    session.commit()
    logger.info("Bulk inserted %d recommendation events", len(objects))
    return objects

