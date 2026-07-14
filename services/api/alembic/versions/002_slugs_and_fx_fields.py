"""slugs_and_fx_fields

Revision ID: 002_slugs
Revises: 001_initial
Create Date: 2026-07-14 05:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_slugs"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("source", sa.Column("source_key", sa.String(length=128), nullable=True))
    op.add_column("source", sa.Column("name_en", sa.String(length=512), nullable=True))
    op.add_column("source", sa.Column("slug", sa.String(length=256), nullable=True))
    op.create_index("ix_source_slug", "source", ["slug"], unique=True)
    op.create_index("ix_source_source_key", "source", ["source_key"], unique=True)

    op.add_column("canonical_listing", sa.Column("slug", sa.String(length=256), nullable=True))
    op.create_index("ix_canonical_listing_slug", "canonical_listing", ["slug"], unique=True)

    op.add_column("administrative_entity", sa.Column("slug", sa.String(length=256), nullable=True))
    op.create_index("ix_administrative_entity_slug", "administrative_entity", ["slug"], unique=True)

    op.add_column("fx_rate", sa.Column("effective_date", sa.Date(), nullable=True))
    op.add_column("fx_rate", sa.Column("raw_payload_hash", sa.String(length=128), nullable=True))
    op.add_column("fx_rate", sa.Column("stale", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("fx_rate", sa.Column("selected_for_display", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("fx_rate", sa.Column("validation_status", sa.String(length=32), nullable=True))
    op.add_column("fx_rate", sa.Column("cross_check_deviation", sa.Numeric(precision=12, scale=8), nullable=True))


def downgrade() -> None:
    op.drop_column("fx_rate", "cross_check_deviation")
    op.drop_column("fx_rate", "validation_status")
    op.drop_column("fx_rate", "selected_for_display")
    op.drop_column("fx_rate", "stale")
    op.drop_column("fx_rate", "raw_payload_hash")
    op.drop_column("fx_rate", "effective_date")
    op.drop_index("ix_administrative_entity_slug", table_name="administrative_entity")
    op.drop_column("administrative_entity", "slug")
    op.drop_index("ix_canonical_listing_slug", table_name="canonical_listing")
    op.drop_column("canonical_listing", "slug")
    op.drop_index("ix_source_source_key", table_name="source")
    op.drop_index("ix_source_slug", table_name="source")
    op.drop_column("source", "slug")
    op.drop_column("source", "name_en")
    op.drop_column("source", "source_key")
