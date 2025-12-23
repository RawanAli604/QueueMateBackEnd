from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from .base import Base

class WaitlistEntryModel(Base):

    __tablename__ = "waitlist_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    status = Column(String, default="waiting")  
    position = Column(Integer, nullable=False)
    estimated_wait_time = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=func.now())
