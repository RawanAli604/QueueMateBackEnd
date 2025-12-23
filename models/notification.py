from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from .base import Base

class NotificationModel(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    status = Column(String, nullable=False)  # status update from waitlist entry
    message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
