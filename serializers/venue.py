from pydantic import BaseModel

class VenueSchema(BaseModel):
    name: str
    location: str
    max_capacity: int
    avg_service_time: int = 0
    
    class Config:
        orm_mode = True

class VenueResponse(VenueSchema):
    id: int
    owner_id: int

    class Config:
        orm_mode = True