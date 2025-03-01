from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SessionBase(SQLModel):
    """Base model for reading sessions."""

    duration: int = Field(description="Duration of the reading session in minutes")
    description: Optional[str] = Field(
        default=None, description="Optional description of what was read"
    )


class Session(SessionBase, table=True):
    """Reading session model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Date and time of the session"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Date the session was updated, if it was"
    )


class SessionCreate(SessionBase):
    """Schema for creating a new reading session."""

    pass


class SessionUpdate(SQLModel):
    """Schema for updating an existing reading session."""

    duration: Optional[int] = None
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionRead(SessionBase):
    """Schema for reading a session."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
