from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class VenueModel(Base):

    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    avg_service_time = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    image_url = Column(String, nullable=True)