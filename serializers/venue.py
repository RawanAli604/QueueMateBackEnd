from pydantic import BaseModel

class VenueSchema(BaseModel):
    name: str
    location: str
    max_capacity: int
    avg_wait_time: int = 0

    class Config:
        orm_mode = True
