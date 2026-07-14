import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    saved_searches: Mapped[list["SavedSearch"]] = relationship(back_populates="user")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")


class SavedSearch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "saved_search"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    query_params: Mapped[dict] = mapped_column(JSONB, nullable=False)

    user: Mapped[User] = relationship(back_populates="saved_searches")


class Favorite(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "canonical_listing_id", name="uq_favorite_user_listing"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    canonical_listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_listing.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="favorites")
    canonical_listing: Mapped["CanonicalListing"] = relationship(back_populates="favorites")


from tsubo_api.models.listings import CanonicalListing  # noqa: E402
