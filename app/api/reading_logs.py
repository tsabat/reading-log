from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.reading_log import ReadingLog as ReadingLogModel
from app.models.reading_log import ReadingLogCreate, ReadingLogRead, ReadingLogUpdate

router = APIRouter(prefix="/reading-logs", tags=["reading-logs"])


@router.post("/", response_model=ReadingLogRead)
def create_reading_log(
    *, reading_log: ReadingLogCreate, db: Session = Depends(get_session)
) -> ReadingLogModel:
    """Create a new reading log."""
    db_reading_log = ReadingLogModel.model_validate(reading_log.model_dump())
    db.add(db_reading_log)
    db.commit()
    db.refresh(db_reading_log)
    return db_reading_log


@router.get("/", response_model=List[ReadingLogRead])
def read_reading_logs(
    *,
    db: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> List[ReadingLogModel]:
    """Get all reading logs with pagination."""
    reading_logs = db.exec(select(ReadingLogModel).offset(offset).limit(limit)).all()
    return reading_logs


@router.get("/{reading_log_id}", response_model=ReadingLogRead)
def read_reading_log(
    *, db: Session = Depends(get_session), reading_log_id: int
) -> ReadingLogModel:
    """Get a specific reading log by ID."""
    reading_log = db.get(ReadingLogModel, reading_log_id)
    if not reading_log:
        raise HTTPException(status_code=404, detail="Reading log not found")
    return reading_log


@router.patch("/{reading_log_id}", response_model=ReadingLogRead)
def update_reading_log(
    *,
    db: Session = Depends(get_session),
    reading_log_id: int,
    reading_log_update: ReadingLogUpdate,
) -> ReadingLogModel:
    """Update a reading log."""
    db_reading_log = db.get(ReadingLogModel, reading_log_id)
    if not db_reading_log:
        raise HTTPException(status_code=404, detail="Reading log not found")

    # Update only the fields that are provided
    update_data = reading_log_update.model_dump(exclude_unset=True)

    # Always set updated_at to current time
    update_data["updated_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_reading_log, key, value)

    db.add(db_reading_log)
    db.commit()
    db.refresh(db_reading_log)
    return db_reading_log


@router.delete("/{reading_log_id}", response_model=ReadingLogRead)
def delete_reading_log(
    *, db: Session = Depends(get_session), reading_log_id: int
) -> ReadingLogModel:
    """Delete a reading log."""
    reading_log = db.get(ReadingLogModel, reading_log_id)
    if not reading_log:
        raise HTTPException(status_code=404, detail="Reading log not found")

    db.delete(reading_log)
    db.commit()
    return reading_log
