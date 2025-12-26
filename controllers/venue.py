from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.venue import VenueModel
from models.user import UserModel
from serializers.venue import VenueSchema, VenueResponse, VenueCreateSchema
from typing import List
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()

@router.get("/venue", response_model=List[VenueSchema])
def get_venues(db: Session = Depends(get_db)):
    return db.query(VenueModel).all()

@router.get("/venue/my", response_model=List[VenueSchema])
def get_my_venues(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Not authorized")

    venues = db.query(VenueModel).filter(
        VenueModel.owner_id == current_user.id
    ).all()

    return venues

@router.get("/venue/{venue_id}", response_model=VenueSchema)
def get_single_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@router.post("/venue", response_model=VenueResponse)
def create_venue(venue: VenueCreateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can create venues")

    # Assign ownership
    new_venue = VenueModel(**venue.dict(), owner_id=current_user.id)
    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)
    return new_venue

@router.put("/venue/{venue_id}", response_model=VenueSchema)
def update_venue(venue_id: int, venue: VenueSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not db_venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    if current_user.role != "staff" or db_venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this venue")

    venue_data = venue.dict(exclude_unset=True)
    for key, value in venue_data.items():
        setattr(db_venue, key, value)

    db.commit()
    db.refresh(db_venue)
    return db_venue

@router.delete("/venue/{venue_id}")
def delete_venue(venue_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not db_venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    if current_user.role != "staff" or db_venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this venue")

    db.delete(db_venue)
    db.commit()
    return {"message": f"Venue with ID {venue_id} has been deleted"}
