from datetime import timedelta
from statistics import median

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DelayReport, utc_now

LIVE_WINDOW_HOURS = 3
HALF_LIFE_MINUTES = 30
ON_TIME_THRESHOLD = 5
RELIABILITY_DAYS = 30


def remove_outliers(items):
    """items is a list of (delay_minutes, reported_at) pairs.
    Drops reports far away from the median. Needs 3+ reports to judge."""
    if len(items) < 3:
        return items
    mid = median([delay for delay, _ in items])
    tolerance = max(20, mid)
    return [(d, t) for d, t in items if abs(d - mid) <= tolerance]


def weighted_average(items, now):
    """Average delay where newer reports count more."""
    total_weight = 0.0
    total = 0.0
    for delay, reported_at in items:
        age_minutes = (now - reported_at).total_seconds() / 60
        weight = 0.5 ** (age_minutes / HALF_LIFE_MINUTES)
        total += delay * weight
        total_weight += weight
    return total / total_weight


def get_live_delay(db: Session, train_number: str, now=None):
    now = now or utc_now()
    since = now - timedelta(hours=LIVE_WINDOW_HOURS)
    stmt = select(DelayReport.delay_minutes, DelayReport.reported_at).where(
        DelayReport.train_number == train_number,
        DelayReport.reported_at >= since,
    )
    items = [(row.delay_minutes, row.reported_at) for row in db.execute(stmt)]
    items = remove_outliers(items)

    if not items:
        return {
            "train_number": train_number,
            "live_delay_minutes": None,
            "based_on_reports": 0,
            "window_hours": LIVE_WINDOW_HOURS,
        }
    return {
        "train_number": train_number,
        "live_delay_minutes": round(weighted_average(items, now)),
        "based_on_reports": len(items),
        "window_hours": LIVE_WINDOW_HOURS,
    }


def get_reliability(db: Session, train_number: str, now=None):
    now = now or utc_now()
    since = now - timedelta(days=RELIABILITY_DAYS)
    stmt = select(DelayReport.delay_minutes).where(
        DelayReport.train_number == train_number,
        DelayReport.reported_at >= since,
    )
    delays = list(db.scalars(stmt))

    if not delays:
        return {
            "train_number": train_number,
            "reliability_score": None,
            "average_delay_minutes": None,
            "total_reports": 0,
            "window_days": RELIABILITY_DAYS,
        }
    on_time = sum(1 for d in delays if d <= ON_TIME_THRESHOLD)
    return {
        "train_number": train_number,
        "reliability_score": round(100 * on_time / len(delays), 1),
        "average_delay_minutes": round(sum(delays) / len(delays), 1),
        "total_reports": len(delays),
        "window_days": RELIABILITY_DAYS,
    }