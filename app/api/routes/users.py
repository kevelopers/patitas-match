import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_authenticated_user, verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


class UserPreferencesSchema(BaseModel):
    size: list[str]
    energy_level: list[str]
    life_stage: list[str]
    has_yard: bool
    role: str


class PrivacyUpdateSchema(BaseModel):
    current_password: str
    new_password: Optional[str] = None
    new_phone: Optional[str] = None

    @field_validator("new_phone")
    def validate_phone_format(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            cleaned_value = str(value).strip()
            if cleaned_value == "":
                return None
            phone_regex = r"^(?:\+?58|0)?(?:412|414|424|416|426)\d{7}$"
            if not re.match(phone_regex, cleaned_value):
                raise ValueError("El formato del numero de telefono no es valido")
            return cleaned_value
        return value


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/foundations")
@router.get("/foundations/")
def get_all_allied_foundations(db: Session = Depends(get_database_session)):
    foundations = (
        db.query(User).filter(User.role == "foundation").order_by(User.name.asc()).all()
    )
    return [{"id": f.id, "name": f.name} for f in foundations]


@router.get("/profile")
@router.get("/profile/")
def get_user_profile_data(current_user: User = Depends(get_authenticated_user)):
    raw_size = getattr(current_user, "size_preference", "") or ""
    raw_energy = getattr(current_user, "energy_preference", "") or ""
    raw_stage = getattr(current_user, "stage_preference", "") or ""

    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "preferences": {
            "size": [s.strip() for s in raw_size.split(",") if s.strip()],
            "energy_level": [e.strip() for e in raw_energy.split(",") if e.strip()],
            "life_stage": [l.strip() for l in raw_stage.split(",") if l.strip()],
            "has_yard": bool(current_user.has_yard),
        },
    }


@router.post("/profile/preferences")
@router.post("/profile/preferences/")
def update_user_profile_preferences(
    payload: UserPreferencesSchema,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User missing")

    setattr(user, "role", payload.role)
    setattr(user, "size_preference", ",".join(payload.size))
    setattr(user, "energy_preference", ",".join(payload.energy_level))
    setattr(user, "stage_preference", ",".join(payload.life_stage))
    setattr(user, "has_yard", payload.has_yard)

    db.commit()
    return {"status": "success"}


@router.post("/profile/privacy")
@router.post("/profile/privacy/")
def update_user_privacy_data(
    payload: PrivacyUpdateSchema,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None or user.hashed_password is None:
        raise HTTPException(status_code=404, detail="User missing")

    if not verify_password(payload.current_password, str(user.hashed_password)):
        raise HTTPException(
            status_code=400, detail="La contraseña actual es incorrecta"
        )

    if payload.new_password and payload.new_password.strip() != "":
        setattr(user, "hashed_password", get_password_hash(payload.new_password))

    if payload.new_phone is not None:
        setattr(user, "phone", payload.new_phone)

    db.commit()
    return {"status": "success"}
