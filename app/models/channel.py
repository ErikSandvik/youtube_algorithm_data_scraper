from __future__ import annotations
from sqlalchemy import String, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Channel(Base):
    """Represents a YouTube channel and its metadata."""
    __tablename__ = "channels"

    # Primary key — YouTube channel ID (manually defined)
    channel_id: Mapped[str] = mapped_column(String, primary_key=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Topic categories from YouTube API
    topic_categories: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Location
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
