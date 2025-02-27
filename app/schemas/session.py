import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionBase(BaseModel):
    """Base schema for Session"""

    date: Optional[datetime.datetime] = None
    duration: int = Field(..., description="Duration of the reading session in minutes", gt=0)


class SessionCreate(SessionBase):
    """Schema for creating a new Session"""

    pass


class SessionUpdate(BaseModel):
    """Schema for updating an existing Session"""

    date: Optional[datetime.datetime] = None
    duration: Optional[int] = Field(None, description="Duration of the reading session in minutes", gt=0)


class SessionResponse(SessionBase):
    """Schema for Session response"""

    id: int
    date: datetime.datetime

    class Config:
        from_attributes = True
