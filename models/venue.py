from sqlalchemy import Column, Integer, String
from .base import Base

class VenueModel(Base):

    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    avg_wait_time = Column(Integer, nullable=True)  # in minutes
