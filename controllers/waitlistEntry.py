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


@router.get("/waitlist/my", response_model=List[WaitlistEntryResponseSchema])
def get_my_waitlist(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    entries = db.query(WaitlistEntryModel).filter(WaitlistEntryModel.user_id == current_user.id).all()
    return entries

@router.get("/waitlist/my/{entry_id}", response_model=WaitlistEntrySchema)
def get_single_waitlist_entry(entry_id: int, db: Session = Depends(get_db),
                              current_user: UserModel = Depends(get_current_user)):
    entry = db.query(WaitlistEntryModel).filter(WaitlistEntryModel.id == entry_id,
                                                WaitlistEntryModel.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return entry

@router.put("/waitlist/my/{entry_id}/cancel", response_model=WaitlistEntryResponseSchema)
def cancel_waitlist_entry(entry_id: int, db: Session = Depends(get_db),
                          current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can cancel their waitlist entries")

    entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.id == entry_id,
        WaitlistEntryModel.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    if entry.status in ["cancelled", "seated"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel an entry with status '{entry.status}'")

    # Set status to cancelled
    entry.status = "cancelled"
    db.commit()
    db.refresh(entry)

    waiting_entries = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == entry.venue_id,
        WaitlistEntryModel.status == "waiting"
    ).order_by(WaitlistEntryModel.position).all()

    for idx, e in enumerate(waiting_entries, start=1):
        e.position = idx
        db.add(e)
    db.commit()

    return entry

def calculate_estimated_wait_time(db: Session, venue_id: int):
    venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not venue:
        return None

    waiting_count = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == venue_id,
        WaitlistEntryModel.status == "waiting"
    ).count()

    return waiting_count * (venue.avg_service_time or 10)

@router.put("/waitlist/{entry_id}/approve", response_model=WaitlistEntryResponseSchema)
def approve_waitlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Only staff can approve join requests
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can approve waitlist requests")

    entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.id == entry_id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    # Ensure staff owns this venue
    venue = db.query(VenueModel).filter(
        VenueModel.id == entry.venue_id,
        VenueModel.owner_id == current_user.id
    ).first()

    if not venue:
        raise HTTPException(status_code=403, detail="You are not allowed to manage this venue")

    if entry.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending entries can be approved")

    # Assign queue position
    current_max_position = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == entry.venue_id,
        WaitlistEntryModel.status == "waiting"
    ).count()

    entry.position = current_max_position + 1
    entry.status = "waiting"
    entry.estimated_wait_time = calculate_estimated_wait_time(db, entry.venue_id)

    db.add(entry)

    notification = NotificationModel(
        user_id=entry.user_id,
        message=f"You are now in the waiting list for {venue.name}. Your position is {entry.position}.",
        created_at=datetime.utcnow()
    )

    db.add(notification)
    db.commit()
    db.refresh(entry)

    return entry