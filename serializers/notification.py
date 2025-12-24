from pydantic import BaseModel
from datetime import datetime

class NotificationSchema(BaseModel):
    id: int
    user_id: int
    venue_id: int
    status: str
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True

class NotificationResponseSchema(BaseModel):
    id: int
    message: str
    created_at: datetime
    read: bool

    class Config:
        orm_mode = True