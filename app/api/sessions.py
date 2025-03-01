from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.session import Session as SessionModel
from app.models.session import SessionCreate, SessionRead, SessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionRead)
def create_session(
    *, session: SessionCreate, db: Session = Depends(get_session)
) -> SessionModel:
    """Create a new reading session."""
    db_session = SessionModel.model_validate(session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/", response_model=List[SessionRead])
def read_sessions(
    *,
    db: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> List[SessionModel]:
    """Get all reading sessions with pagination."""
    sessions = db.exec(select(SessionModel).offset(offset).limit(limit)).all()
    return sessions


@router.get("/{session_id}", response_model=SessionRead)
def read_session(
    *, db: Session = Depends(get_session), session_id: int
) -> SessionModel:
    """Get a specific reading session by ID."""
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=SessionRead)
def update_session(
    *,
    db: Session = Depends(get_session),
    session_id: int,
    session_update: SessionUpdate,
) -> SessionModel:
    """Update a reading session."""
    db_session = db.get(SessionModel, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update only the fields that are provided
    update_data = session_update.model_dump(exclude_unset=True)

    # Always set updated_at to current time
    update_data["updated_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_session, key, value)

    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/{session_id}", response_model=SessionRead)
def delete_session(
    *, db: Session = Depends(get_session), session_id: int
) -> SessionModel:
    """Delete a reading session."""
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return session
