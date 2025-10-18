from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, BigInteger, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

class Video(Base):
    """Represents a YouTube video and its metadata."""
    __tablename__ = "videos"

    # Primary key — YouTube video ID (manually defined)
    video_id: Mapped[str] = mapped_column(String(32), primary_key=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # Iteration recommended by YouTube
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Channel info
    channel_id: Mapped[str] = mapped_column(String(64), nullable=False)
    channel_title: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Tags (JSON array)
    tags_json: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)

    # Category & timestamps
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Additional metadata
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)  # e.g., 'en', 'no'
    duration_iso: Mapped[str | None] = mapped_column(String(32), nullable=True)  # e.g., 'PT3M45S'

    # Metrics
    view_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    like_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    comment_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

Index("ix_videos_channel_id", Video.channel_id)
Index("ix_videos_published_at", Video.published_at)