import uuid
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tsubo_contracts.enums import (
    ConditionCategory,
    ListingStatus,
    LocationPrecision,
    PriceKind,
    PropertyType,
    TransactionType,
)

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CrawlRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "crawl_run"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped["Source"] = relationship(back_populates="crawl_runs")
    raw_snapshots: Mapped[list["RawSnapshot"]] = relationship(back_populates="crawl_run")


class RawSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "raw_snapshot"

    crawl_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_run.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    s3_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    crawl_run: Mapped[CrawlRun | None] = relationship(back_populates="raw_snapshots")
    source: Mapped["Source"] = relationship(back_populates="raw_snapshots")
    source_listing_records: Mapped[list["SourceListingRecord"]] = relationship(
        back_populates="raw_snapshot",
    )


class SourceListingRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "source_listing_record"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw_snapshot.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_listing_id: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    source: Mapped["Source"] = relationship(back_populates="source_listing_records")
    raw_snapshot: Mapped[RawSnapshot | None] = relationship(
        back_populates="source_listing_records",
    )
    canonical_listings: Mapped[list["CanonicalListing"]] = relationship(
        back_populates="source_listing_record",
    )


class CanonicalListing(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "canonical_listing"

    slug: Mapped[str | None] = mapped_column(String(256), nullable=True, unique=True, index=True)
    source_listing_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_listing_record.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    administrative_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("administrative_entity.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[ListingStatus] = mapped_column(String(64), nullable=False, index=True)
    transaction_type: Mapped[TransactionType] = mapped_column(String(64), nullable=False)
    property_type: Mapped[PropertyType] = mapped_column(String(64), nullable=False, index=True)
    price_jpy: Mapped[Decimal | None] = mapped_column(Numeric(20, 0), nullable=True)
    price_kind: Mapped[PriceKind] = mapped_column(String(64), nullable=False)
    monthly_rent_jpy: Mapped[Decimal | None] = mapped_column(Numeric(20, 0), nullable=True)
    area_sqm: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    land_area_sqm: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    location_precision: Mapped[LocationPrecision] = mapped_column(String(64), nullable=False)
    condition_category: Mapped[ConditionCategory] = mapped_column(String(64), nullable=False)
    geom: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    address_ja: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    address_en: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    title_ja: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    title_en: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description_ja: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    source_listing_record: Mapped[SourceListingRecord | None] = relationship(
        back_populates="canonical_listings",
    )
    source: Mapped["Source"] = relationship(back_populates="canonical_listings")
    administrative_entity: Mapped["AdministrativeEntity | None"] = relationship()
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="canonical_listing")
    field_provenance: Mapped[list["FieldProvenance"]] = relationship(
        back_populates="canonical_listing",
    )
    duplicate_candidates_a: Mapped[list["DuplicateCandidate"]] = relationship(
        foreign_keys="DuplicateCandidate.listing_a_id",
        back_populates="listing_a",
    )
    duplicate_candidates_b: Mapped[list["DuplicateCandidate"]] = relationship(
        foreign_keys="DuplicateCandidate.listing_b_id",
        back_populates="listing_b",
    )


from tsubo_api.models.administrative import AdministrativeEntity  # noqa: E402
from tsubo_api.models.provenance import (  # noqa: E402
    DuplicateCandidate,
    FieldProvenance,
)
from tsubo_api.models.sources import Source  # noqa: E402
from tsubo_api.models.users import Favorite  # noqa: E402
