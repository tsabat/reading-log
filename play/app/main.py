import datetime

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.db.connection import setup_connection
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - runs on startup
    setup_connection()
    yield
    # Cleanup - runs on shutdown
    # Add any cleanup code here if needed


app = FastAPI(title="Reading Tracker API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sessions", response_model=List[SessionResponse])
def get_sessions():
    """Get all reading sessions"""
    try:
        sessions = list(Session.select())
        return [
            SessionResponse(id=session.id, date=session.date, duration=session.duration)
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(session: SessionCreate):
    """Create a new reading session"""
    try:
        new_session = Session(
            date=session.date or datetime.datetime.now(), duration=session.duration
        )
        return SessionResponse(
            id=new_session.id, date=new_session.date, duration=new_session.duration
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int):
    """Get a specific reading session by ID"""
    try:
        session = Session.get(session_id)
        return SessionResponse(
            id=session.id, date=session.date, duration=session.duration
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")


@app.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, session_update: SessionUpdate):
    """Update a reading session"""
    try:
        session = Session.get(session_id)

        if session_update.date is not None:
            session.date = session_update.date
        if session_update.duration is not None:
            session.duration = session_update.duration

        return SessionResponse(
            id=session.id, date=session.date, duration=session.duration
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")


@app.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int):
    """Delete a reading session"""
    try:
        session = Session.get(session_id)
        session.destroySelf()
        return None
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")
