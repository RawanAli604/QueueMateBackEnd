from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from sqlalchemy import func
from datetime import datetime
from models.user import UserModel
from models.venue import VenueModel
from models.waitlistEntry import WaitlistEntryModel
from models.notification import NotificationModel
from serializers.waitListEntry import WaitlistEntrySchema, WaitlistEntryResponseSchema
from dependencies.get_current_user import get_current_user


router = APIRouter()

def recalc_queue_positions_and_eta(db: Session, venue_id: int):
    venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not venue:
        return

    waiting_entries = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == venue_id,
        WaitlistEntryModel.status == "waiting"
    ).order_by(WaitlistEntryModel.position).all()

    avg_time = venue.avg_service_time or 10
    running_time = 0

    for idx, entry in enumerate(waiting_entries, start=1):
        old_position = entry.position

        entry.position = idx
        entry.estimated_wait_time = running_time
        running_time += avg_time
        db.add(entry)

        # Notify ONLY if their position changed
        if old_position != idx:
            note = NotificationModel(
                user_id=entry.user_id,
                message=f"Your position in the queue at {venue.name} is now {idx}.",
                created_at=datetime.utcnow()
            )
            db.add(note)

    db.commit()

def create_notification(db: Session, user_id: int, venue_id: int, message: str):
    note = NotificationModel(
        user_id=user_id,
        venue_id=venue_id,
        message=message,
        timestamp=datetime.utcnow()
    )
    db.add(note)
    db.commit()

@router.post("/waitlist", response_model=WaitlistEntryResponseSchema)
def join_waitlist(
    entry: WaitlistEntrySchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can join the waitlist")

    venue = db.query(VenueModel).filter(VenueModel.id == entry.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Prevent duplicate entries (pending or waiting)
    exists = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.user_id == current_user.id,
        WaitlistEntryModel.venue_id == venue.id,
        WaitlistEntryModel.status.in_(["pending", "waiting"])
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="You already have a waitlist entry for this venue")

    # Get current max position for this venue's active waitlist
    max_position = db.query(func.max(WaitlistEntryModel.position)).filter(
        WaitlistEntryModel.venue_id == venue.id,
        WaitlistEntryModel.status.in_(["pending", "waiting"])
    ).scalar()
    new_position = (max_position or 0) + 1

    # Create new waitlist entry
    new_entry = WaitlistEntryModel(
        user_id=current_user.id,
        venue_id=venue.id,
        status="pending",
        position=new_position,
        estimated_wait_time=None,
        timestamp=datetime.utcnow()
    )

    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to join waitlist") from e

    return new_entry

@router.get("/waitlist/my", response_model=List[WaitlistEntryResponseSchema])
def get_my_waitlist(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.user_id == current_user.id
    ).order_by(WaitlistEntryModel.timestamp.desc()).all()


@router.get("/waitlist/my/{entry_id}", response_model=WaitlistEntryResponseSchema)
def get_single_waitlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.id == entry_id,
        WaitlistEntryModel.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    return entry

@router.put("/waitlist/my/{entry_id}/cancel", response_model=WaitlistEntryResponseSchema)
def cancel_waitlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can cancel their entries")

    entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.id == entry_id,
        WaitlistEntryModel.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    if entry.status not in ["pending", "waiting"]:
        raise HTTPException(status_code=400, detail="This entry can no longer be cancelled")

    status_before = entry.status
    entry.status = "cancelled"
    db.commit()

    if status_before == "waiting":
      recalc_queue_positions_and_eta(db, entry.venue_id)

    create_notification(db, entry.user_id, entry.venue_id, "Your waitlist request was cancelled.")
    db.refresh(entry)
    return entry

@router.put("/waitlist/{entry_id}/approve", response_model=WaitlistEntryResponseSchema)
def approve_waitlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can approve waitlist requests")

    entry = db.query(WaitlistEntryModel).filter(WaitlistEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    venue = db.query(VenueModel).filter(
        VenueModel.id == entry.venue_id,
        VenueModel.owner_id == current_user.id
    ).first()

    if not venue:
        raise HTTPException(status_code=403, detail="You cannot manage this venue")

    if entry.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending entries can be approved")

    # Assign queue position
    max_pos = db.query(func.max(WaitlistEntryModel.position)).filter(
        WaitlistEntryModel.venue_id == entry.venue_id,
        WaitlistEntryModel.status == "waiting"
    ).scalar() or 0

    entry.position = max_pos + 1
    entry.status = "waiting"
    entry.estimated_wait_time = (entry.position - 1) * (venue.avg_service_time or 10)

    db.commit()

    create_notification(
        db,
        entry.user_id,
        f"You were added to the waiting list for {venue.name}. Position: {entry.position}"
    )

    db.refresh(entry)
    return entry


@router.put("/waitlist/{entry_id}/seated", response_model=WaitlistEntryResponseSchema)
def mark_as_seated(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can update waitlist status")

    entry = db.query(WaitlistEntryModel).filter(WaitlistEntryModel.id == entry_id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    venue = db.query(VenueModel).filter(
        VenueModel.id == entry.venue_id,
        VenueModel.owner_id == current_user.id
    ).first()

    if not venue:
        raise HTTPException(status_code=403, detail="You cannot manage this venue")

    if entry.status != "waiting":
        raise HTTPException(status_code=400, detail="Only waiting users can be marked as seated")

    entry.status = "seated"
    db.commit()

    recalc_queue_positions_and_eta(db, entry.venue_id)

    create_notification(db, entry.user_id, "You have been seated. Enjoy!")

    db.refresh(entry)
    return entry

@router.put("/waitlist/{entry_id}/reject", response_model=WaitlistEntryResponseSchema)
def reject_waitlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can reject waitlist requests")

    entry = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.id == entry_id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    venue = db.query(VenueModel).filter(
        VenueModel.id == entry.venue_id,
        VenueModel.owner_id == current_user.id
    ).first()

    if not venue:
        raise HTTPException(status_code=403, detail="You are not allowed to manage this venue")

    # Can only reject pending requests
    if entry.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending entries can be rejected")

    entry.status = "rejected"
    entry.position = None
    entry.estimated_wait_time = None

    db.add(entry)

    notification = NotificationModel(
        user_id=entry.user_id,
        message=f"Your waitlist request at {venue.name} was rejected.",
        timestamp=datetime.utcnow()
    )

    db.add(notification)
    db.commit()
    db.refresh(entry)

    return entry

@router.get("/waitlist/venue/{venue_id}", response_model=List[WaitlistEntryResponseSchema])
def get_waitlist_for_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff can view venue waitlists")

    venue = db.query(VenueModel).filter(
        VenueModel.id == venue_id,
        VenueModel.owner_id == current_user.id
    ).first()

    if not venue:
        raise HTTPException(status_code=403, detail="You do not manage this venue")

    waitlist_entries = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == venue_id
    ).all()

    return waitlist_entries


@router.get("/waitlist/venue/count/{venue_id}")
def get_waitlist_count_for_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    count = db.query(WaitlistEntryModel).filter(
        WaitlistEntryModel.venue_id == venue_id,
        WaitlistEntryModel.status == "waiting"
    ).count()

    return {"venue_id": venue_id, "waiting_count": count}