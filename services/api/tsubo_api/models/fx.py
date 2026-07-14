from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from tsubo_api.database import Base
from tsubo_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class FXRate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "fx_rate"

    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="JPY", index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    raw_payload_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    selected_for_display: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cross_check_deviation: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)


class FXProviderHealth(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "fx_provider_health"

    provider: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
