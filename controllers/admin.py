from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from models.user import UserModel
from models.venue import VenueModel
from serializers.user import UserResponseSchema
from serializers.venue import VenueSchema
from typing import List
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()


# Only admin can access this
def admin_required(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/users", response_model=List[UserResponseSchema])
def get_all_users(db: Session = Depends(get_db), admin: UserModel = Depends(admin_required)):
    return db.query(UserModel).all()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: UserModel = Depends(admin_required)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}

@router.get("/admin/analytics")
def get_admin_analytics(db: Session = Depends(get_db), admin: UserModel = Depends(admin_required)):
    total_users = db.query(UserModel).count()
    total_staff = db.query(UserModel).filter(UserModel.role == "staff").count()
    total_customers = db.query(UserModel).filter(UserModel.role == "customer").count()
    total_venues = db.query(VenueModel).count()

    return {
        "total_users": total_users,
        "total_staff": total_staff,
        "total_customers": total_customers,
        "total_venues": total_venues
    }

@router.delete("/venues/{venue_id}")
def delete_any_venue(venue_id: int, db: Session = Depends(get_db), admin: UserModel = Depends(admin_required)):
    venue = db.query(VenueModel).filter(VenueModel.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    db.delete(venue)
    db.commit()
    return {"message": f"Venue {venue.name} deleted successfully"}
