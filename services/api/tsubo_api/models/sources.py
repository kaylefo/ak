import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tsubo_contracts.enums import AccessMode, CoverageState, SourceClass, SourceHealth

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Source(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "source"

    source_key: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    slug: Mapped[str | None] = mapped_column(String(256), nullable=True, unique=True, index=True)
    source_class: Mapped[SourceClass] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(512), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    access_mode: Mapped[AccessMode] = mapped_column(String(64), nullable=False)
    health: Mapped[SourceHealth] = mapped_column(
        String(64),
        nullable=False,
        default=SourceHealth.UNKNOWN,
        index=True,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    jurisdictions: Mapped[list["SourceJurisdiction"]] = relationship(back_populates="source")
    crawl_runs: Mapped[list["CrawlRun"]] = relationship(back_populates="source")
    raw_snapshots: Mapped[list["RawSnapshot"]] = relationship(back_populates="source")
    source_listing_records: Mapped[list["SourceListingRecord"]] = relationship(
        back_populates="source",
    )
    canonical_listings: Mapped[list["CanonicalListing"]] = relationship(back_populates="source")


class SourceJurisdiction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "source_jurisdiction"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    administrative_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("administrative_entity.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coverage_state: Mapped[CoverageState] = mapped_column(String(64), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[Source] = relationship(back_populates="jurisdictions")
    administrative_entity: Mapped["AdministrativeEntity"] = relationship(
        back_populates="source_jurisdictions",
    )


from tsubo_api.models.administrative import AdministrativeEntity  # noqa: E402
from tsubo_api.models.listings import (  # noqa: E402
    CanonicalListing,
    CrawlRun,
    RawSnapshot,
    SourceListingRecord,
)
