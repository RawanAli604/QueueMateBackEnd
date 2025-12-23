
from typing import Optional
from pydantic import BaseModel

class WaitlistEntrySchema(BaseModel):
    user_id: int
    venue_id: int
    status: str = "waiting"
    position: int
    # will be calculated later that's why it's set to none
    estimated_wait_time: Optional[int] = None

    class Config:
        orm_mode = True

class WaitlistEntryResponseSchema(WaitlistEntrySchema):
    id: int
    timestamp: str

    class Config:
        orm_mode = True