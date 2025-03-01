from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ReadingLogBase(SQLModel):
    """Base model for reading logs."""

    duration: int = Field(description="Duration of the reading session in minutes")
    description: Optional[str] = Field(
        default=None, description="Optional description of what was read"
    )


class ReadingLog(ReadingLogBase, table=True):
    """Reading log model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Date and time of the reading log"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Date the reading log was updated, if it was"
    )


class ReadingLogCreate(ReadingLogBase):
    """Schema for creating a new reading log."""

    pass


class ReadingLogUpdate(SQLModel):
    """Schema for updating an existing reading log."""

    duration: Optional[int] = None
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReadingLogRead(ReadingLogBase):
    """Schema for reading a reading log."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
