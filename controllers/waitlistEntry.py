from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import UserModel
from models.venue import VenueModel
from models.waitlistEntry import WaitlistEntryModel
from models.notification import NotificationModel
from serializers.waitListEntry import WaitlistEntrySchema, WaitlistEntryResponseSchema
from dependencies.get_current_user import get_current_user


router = APIRouter()

@router.post("/waitlist", response_model=WaitlistEntryResponseSchema)
def join_waitlist(entry: WaitlistEntrySchema, db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can join the waitlist")

    venue = db.query(VenueModel).filter(VenueModel.id == entry.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Check if the user already has an active entry for this venue
    existing_entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.user_id == current_user.id,
        WaitlistEntryModel.venue_id == venue.id,
        WaitlistEntryModel.status.in_(["pending", "waiting"])
    ).first()

    if existing_entry:
        raise HTTPException(status_code=400, detail="You are already on the waitlist for this venue")

    waiting_entries = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == venue.id,
        WaitlistEntryModel.status == "waiting"
    ).order_by(WaitlistEntryModel.position).all()

    position = len(waiting_entries) + 1
    estimated_wait_time = sum(e.estimated_wait_time or venue.avg_service_time for e in waiting_entries)

    new_entry = WaitlistEntryModel(
        user_id=current_user.id,
        venue_id=venue.id,
        status="pending",
        position=position,
        estimated_wait_time=estimated_wait_time
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry
