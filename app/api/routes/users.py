from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserPreference
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserPreferenceCreate,
    UserPreferenceResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user.id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(id=user.id, role=user.role, name=user.name, phone=user.phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/{user_id}/preferences", response_model=UserPreferenceResponse)
def define_user_preferences(
    user_id: str, preference: UserPreferenceCreate, db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_preference = (
        db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    )
    if existing_preference:
        raise HTTPException(
            status_code=400, detail="Preferences already exist for this user"
        )

    new_preference = UserPreference(
        user_id=user_id,
        preferred_size=preference.preferred_size,
        preferred_energy=preference.preferred_energy,
        has_yard=preference.has_yard,
    )
    db.add(new_preference)
    db.commit()
    db.refresh(new_preference)
    return new_preference
