import random
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DelayReport, utc_now

# train number -> (station code, typical delay in minutes)
DEMO_TRAINS = {
    "12604": ("MAS", 18),
    "12622": ("TBM", 4),
    "12658": ("CGL", 30),
}


def seed_demo_data(db: Session) -> int:
    """Fills an EMPTY database with sample reports. Returns how many were added."""
    if db.scalar(select(func.count()).select_from(DelayReport)):
        return 0

    rng = random.Random(42)
    now = utc_now()
    reports = []
    for train, (station, typical) in DEMO_TRAINS.items():
        # a few fresh reports so "live delay" has something to show
        ages = [10, 25, 50, 80, 120]  # minutes ago
        # plus older history for the reliability score
        ages += [days * 24 * 60 + rng.randint(0, 600) for days in range(1, 21)]
        for age in ages:
            delay = max(0, round(rng.gauss(typical, typical * 0.4)))
            reports.append(
                DelayReport(
                    train_number=train,
                    station_code=station,
                    delay_minutes=min(delay, 720),
                    reported_at=now - timedelta(minutes=age),
                )
            )
    db.add_all(reports)
    db.commit()
    return len(reports)