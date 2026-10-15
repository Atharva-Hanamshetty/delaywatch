from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db
from app.services import stats
from app.services.ratelimit import limit_reports

Base.metadata.create_all(bind=engine)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="DelayWatch", description="Crowdsourced train delay tracker")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/reports",
    response_model=schemas.ReportOut,
    status_code=201,
    dependencies=[Depends(limit_reports)],
)
def create_report(payload: schemas.ReportCreate, db: Session = Depends(get_db)):
    report = models.DelayReport(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@app.get("/trains/{train_number}/reports", response_model=list[schemas.ReportOut])
def list_reports(train_number: str, db: Session = Depends(get_db)):
    stmt = (
        select(models.DelayReport)
        .where(models.DelayReport.train_number == train_number)
        .order_by(desc(models.DelayReport.reported_at))
        .limit(50)
    )
    return db.scalars(stmt).all()


@app.get("/trains/{train_number}/live")
def live_delay(train_number: str, db: Session = Depends(get_db)):
    return stats.get_live_delay(db, train_number)


@app.get("/trains/{train_number}/reliability")
def reliability(train_number: str, db: Session = Depends(get_db)):
    return stats.get_reliability(db, train_number)