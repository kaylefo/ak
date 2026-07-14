import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tsubo_contracts.enums import TranslationState

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Translation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "translation"

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_locale: Mapped[str] = mapped_column(String(16), nullable=False)
    target_locale: Mapped[str] = mapped_column(String(16), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[TranslationState] = mapped_column(String(64), nullable=False, index=True)


class FieldProvenance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "field_provenance"

    canonical_listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_listing.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_listing_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_listing_record.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    canonical_listing: Mapped["CanonicalListing"] = relationship(back_populates="field_provenance")


class DuplicateCandidate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "duplicate_candidate"

    listing_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_listing.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    listing_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_listing.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    match_reasons: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    listing_a: Mapped["CanonicalListing"] = relationship(
        foreign_keys=[listing_a_id],
        back_populates="duplicate_candidates_a",
    )
    listing_b: Mapped["CanonicalListing"] = relationship(
        foreign_keys=[listing_b_id],
        back_populates="duplicate_candidates_b",
    )


from tsubo_api.models.listings import CanonicalListing  # noqa: E402
