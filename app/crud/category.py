from __future__ import annotations
import logging
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category

logger = logging.getLogger(__name__)


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    return session.query(Category).filter(Category.name == name).one_or_none()

def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    return session.get(Category, category_id)

def add_category(session: Session, name: str) -> Category:
    cat = Category(name=name)
    session.add(cat)
    try:
        session.commit()
        session.refresh(cat)
        logger.info("Inserted category name=%s id=%s", cat.name, cat.id)
        return cat
    except IntegrityError as e:
        session.rollback()
        logger.error("Category insert failed (duplicate name?): %s", e)
        raise


def get_or_create_category(session: Session, name: str) -> Category:
    existing = get_category_by_name(session, name)
    if existing:
        return existing
    try:
        return add_category(session, name)
    except IntegrityError:
        session.rollback()
        return get_category_by_name(session, name)

