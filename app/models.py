from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DelayReport(Base):
    __tablename__ = "delay_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(String(5), index=True)
    station_code: Mapped[str] = mapped_column(String(5))
    delay_minutes: Mapped[int] = mapped_column(Integer)
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)