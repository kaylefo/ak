"""initial_schema

Revision ID: 001_initial
Revises:
Create Date: 2026-07-14 04:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "administrative_entity",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("code", sa.String(length=64), nullable=True),
        sa.Column("canonical_name", sa.String(length=512), nullable=False),
        sa.Column("canonical_name_en", sa.String(length=512), nullable=True),
        sa.Column("geom", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["administrative_entity.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_administrative_entity_code", "administrative_entity", ["code"])
    op.create_index("ix_administrative_entity_entity_type", "administrative_entity", ["entity_type"])
    op.create_index("ix_administrative_entity_parent_id", "administrative_entity", ["parent_id"])

    op.create_table(
        "source",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("base_url", sa.String(length=2048), nullable=True),
        sa.Column("access_mode", sa.String(length=64), nullable=False),
        sa.Column("health", sa.String(length=64), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_health", "source", ["health"])
    op.create_index("ix_source_source_class", "source", ["source_class"])

    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_email", "user", ["email"])

    op.create_table(
        "fx_provider_health",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider"),
    )
    op.create_index("ix_fx_provider_health_provider", "fx_provider_health", ["provider"])

    op.create_table(
        "fx_rate",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Numeric(precision=24, scale=12), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fx_rate_base_currency", "fx_rate", ["base_currency"])
    op.create_index("ix_fx_rate_fetched_at", "fx_rate", ["fetched_at"])
    op.create_index("ix_fx_rate_provider", "fx_rate", ["provider"])
    op.create_index("ix_fx_rate_quote_currency", "fx_rate", ["quote_currency"])

    op.create_table(
        "translation",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("source_locale", sa.String(length=16), nullable=False),
        sa.Column("target_locale", sa.String(length=16), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("translated_text", sa.Text(), nullable=True),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_translation_entity_id", "translation", ["entity_id"])
    op.create_index("ix_translation_entity_type", "translation", ["entity_type"])
    op.create_index("ix_translation_state", "translation", ["state"])

    op.create_table(
        "coverage_assessment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("administrative_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coverage_state", sa.String(length=64), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("assessed_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["administrative_entity_id"],
            ["administrative_entity.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_coverage_assessment_administrative_entity_id",
        "coverage_assessment",
        ["administrative_entity_id"],
    )
    op.create_index("ix_coverage_assessment_coverage_state", "coverage_assessment", ["coverage_state"])

    op.create_table(
        "source_jurisdiction",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("administrative_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coverage_state", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["administrative_entity_id"],
            ["administrative_entity.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_source_jurisdiction_administrative_entity_id",
        "source_jurisdiction",
        ["administrative_entity_id"],
    )
    op.create_index("ix_source_jurisdiction_coverage_state", "source_jurisdiction", ["coverage_state"])
    op.create_index("ix_source_jurisdiction_source_id", "source_jurisdiction", ["source_id"])

    op.create_table(
        "crawl_run",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_found", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crawl_run_source_id", "crawl_run", ["source_id"])
    op.create_index("ix_crawl_run_status", "crawl_run", ["status"])

    op.create_table(
        "raw_snapshot",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crawl_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("s3_key", sa.String(length=1024), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["crawl_run_id"], ["crawl_run.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_snapshot_content_hash", "raw_snapshot", ["content_hash"])
    op.create_index("ix_raw_snapshot_crawl_run_id", "raw_snapshot", ["crawl_run_id"])
    op.create_index("ix_raw_snapshot_source_id", "raw_snapshot", ["source_id"])

    op.create_table(
        "source_listing_record",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_listing_id", sa.String(length=512), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["raw_snapshot_id"], ["raw_snapshot.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_listing_record_raw_snapshot_id", "source_listing_record", ["raw_snapshot_id"])
    op.create_index("ix_source_listing_record_source_id", "source_listing_record", ["source_id"])
    op.create_index("ix_source_listing_record_source_listing_id", "source_listing_record", ["source_listing_id"])

    op.create_table(
        "canonical_listing",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_listing_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("administrative_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("transaction_type", sa.String(length=64), nullable=False),
        sa.Column("property_type", sa.String(length=64), nullable=False),
        sa.Column("price_jpy", sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column("price_kind", sa.String(length=64), nullable=False),
        sa.Column("monthly_rent_jpy", sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column("area_sqm", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("land_area_sqm", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("location_precision", sa.String(length=64), nullable=False),
        sa.Column("condition_category", sa.String(length=64), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("address_ja", sa.String(length=1024), nullable=True),
        sa.Column("address_en", sa.String(length=1024), nullable=True),
        sa.Column("title_ja", sa.String(length=1024), nullable=True),
        sa.Column("title_en", sa.String(length=1024), nullable=True),
        sa.Column("description_ja", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("layout", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["administrative_entity_id"],
            ["administrative_entity.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_listing_record_id"],
            ["source_listing_record.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_canonical_listing_administrative_entity_id",
        "canonical_listing",
        ["administrative_entity_id"],
    )
    op.create_index("ix_canonical_listing_property_type", "canonical_listing", ["property_type"])
    op.create_index("ix_canonical_listing_source_id", "canonical_listing", ["source_id"])
    op.create_index(
        "ix_canonical_listing_source_listing_record_id",
        "canonical_listing",
        ["source_listing_record_id"],
    )
    op.create_index("ix_canonical_listing_status", "canonical_listing", ["status"])

    op.create_table(
        "saved_search",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("query_params", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_search_user_id", "saved_search", ["user_id"])

    op.create_table(
        "favorite",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("canonical_listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["canonical_listing_id"], ["canonical_listing.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "canonical_listing_id", name="uq_favorite_user_listing"),
    )
    op.create_index("ix_favorite_canonical_listing_id", "favorite", ["canonical_listing_id"])
    op.create_index("ix_favorite_user_id", "favorite", ["user_id"])

    op.create_table(
        "field_provenance",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("canonical_listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("source_value", sa.Text(), nullable=True),
        sa.Column("normalized_value", sa.Text(), nullable=True),
        sa.Column("source_listing_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["canonical_listing_id"], ["canonical_listing.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_listing_record_id"],
            ["source_listing_record.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_field_provenance_canonical_listing_id", "field_provenance", ["canonical_listing_id"])
    op.create_index("ix_field_provenance_field_name", "field_provenance", ["field_name"])

    op.create_table(
        "duplicate_candidate",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_a_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("similarity_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("match_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["listing_a_id"], ["canonical_listing.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["listing_b_id"], ["canonical_listing.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_duplicate_candidate_listing_a_id", "duplicate_candidate", ["listing_a_id"])
    op.create_index("ix_duplicate_candidate_listing_b_id", "duplicate_candidate", ["listing_b_id"])
    op.create_index("ix_duplicate_candidate_status", "duplicate_candidate", ["status"])


def downgrade() -> None:
    op.drop_table("duplicate_candidate")
    op.drop_table("field_provenance")
    op.drop_table("favorite")
    op.drop_table("saved_search")
    op.drop_table("canonical_listing")
    op.drop_table("source_listing_record")
    op.drop_table("raw_snapshot")
    op.drop_table("crawl_run")
    op.drop_table("source_jurisdiction")
    op.drop_table("coverage_assessment")
    op.drop_table("translation")
    op.drop_table("fx_rate")
    op.drop_table("fx_provider_health")
    op.drop_table("user")
    op.drop_table("source")
    op.drop_table("administrative_entity")
