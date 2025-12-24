from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import UserModel
from models.notification import NotificationModel
from dependencies.get_current_user import get_current_user
from serializers.notification import NotificationResponseSchema

router = APIRouter()

@router.get("/notifications", response_model=List[NotificationResponseSchema])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    notifications = db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id
    ).order_by(NotificationModel.created_at.desc()).all()
    return notifications

@router.put("/notifications/{notification_id}/read", response_model=NotificationResponseSchema)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification