from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WaitlistEntrySchema(BaseModel):
    venue_id: int  # customer sends only venue_id

class WaitlistEntryResponseSchema(BaseModel):
    id: int
    user_id: int
    venue_id: int
    status: str
    position: int
    estimated_wait_time: Optional[int] = None
    timestamp: datetime

    class Config:
        orm_mode = True

class WaitlistEntryUpdateSchema(BaseModel):
    status: Optional[str]
    position: Optional[int]
    estimated_wait_time: Optional[int]

    class Config:
        orm_mode = True


