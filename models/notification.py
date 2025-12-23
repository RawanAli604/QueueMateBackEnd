from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from .base import Base

class NotificationModel(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waitlist_entry_id = Column(Integer, ForeignKey("waitlist_entries.id"), nullable=False)
    message = Column(String, nullable=False)
    # pending, sent, failed
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=func.now())
    sent_at = Column(DateTime, nullable=True)
