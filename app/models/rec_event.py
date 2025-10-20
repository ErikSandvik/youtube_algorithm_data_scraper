from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.models.base import Base


class RecEvent(Base):
    """Represents a single recommendation event that occurred during a crawl."""
    __tablename__ = "rec_events"

    # Unique event ID (auto-incrementing)
    id = Column(BigInteger, primary_key=True)

    # ID for the crawler run session
    run_id = Column(UUID(as_uuid=True), nullable=False)

    # The "depth" of the recommendation in the click chain
    iteration = Column(Integer, nullable=False)

    # The video being watched when the recommendation appeared (nullable for homepage recs)
    source_video_id = Column(Text, nullable=True)

    # The video that was recommended
    video_id = Column(
        Text, ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False
    )

    # The rank of the recommendation on the page (0-based)
    position = Column(Integer)

    # Timestamp of when the event was recorded
    collected_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("id"),)
