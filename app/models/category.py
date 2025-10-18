from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from .base import Base


class Category(Base):
    """Represents a YouTube video category."""
    __tablename__ = "categories"

    # Primary key — YouTube category ID (manually defined)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Category name
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Category(id={self.id!r}, name={self.name!r})"

