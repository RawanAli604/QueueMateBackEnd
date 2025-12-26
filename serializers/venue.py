from pydantic import BaseModel
from typing import Optional

class VenueSchema(BaseModel):
    id: int
    name: str
    location: str
    max_capacity: int
    avg_service_time: int = 0
    image_url: Optional[str] = None 
    
    class Config:
        orm_mode = True

class VenueCreateSchema(BaseModel):
    name: str
    location: str
    max_capacity: int
    avg_service_time: int = 0
    image_url: Optional[str] = None 
    
    class Config:
        orm_mode = True

class VenueResponse(VenueSchema):
    id: int
    owner_id: int

    class Config:
        orm_mode = True