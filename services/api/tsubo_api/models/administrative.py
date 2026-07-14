import uuid
from datetime import date

from geoalchemy2 import Geometry
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tsubo_contracts.enums import CoverageState, EntityType

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AdministrativeEntity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "administrative_entity"

    entity_type: Mapped[EntityType] = mapped_column(String(64), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("administrative_entity.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    slug: Mapped[str | None] = mapped_column(String(256), nullable=True, unique=True, index=True)
    canonical_name: Mapped[str] = mapped_column(String(512), nullable=False)
    canonical_name_en: Mapped[str | None] = mapped_column(String(512), nullable=True)
    geom: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326),
        nullable=True,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    parent: Mapped["AdministrativeEntity | None"] = relationship(
        "AdministrativeEntity",
        remote_side="AdministrativeEntity.id",
        back_populates="children",
    )
    children: Mapped[list["AdministrativeEntity"]] = relationship(
        "AdministrativeEntity",
        back_populates="parent",
    )
    coverage_assessments: Mapped[list["CoverageAssessment"]] = relationship(
        back_populates="administrative_entity",
    )
    source_jurisdictions: Mapped[list["SourceJurisdiction"]] = relationship(
        back_populates="administrative_entity",
    )


class CoverageAssessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "coverage_assessment"

    administrative_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("administrative_entity.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coverage_state: Mapped[CoverageState] = mapped_column(String(64), nullable=False, index=True)
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    administrative_entity: Mapped[AdministrativeEntity] = relationship(
        back_populates="coverage_assessments",
    )
