from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.waitlistEntry import WaitlistEntryModel
from models.user import UserModel
from serializers.waitListEntry import WaitlistEntrySchema, WaitlistEntryResponseSchema
from dependencies.get_current_user import get_current_user

router = APIRouter()

