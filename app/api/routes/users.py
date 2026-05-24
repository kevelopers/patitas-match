from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


class UserPreferencesSchema(BaseModel):
    size: list[str]
    energy_level: list[str]
    life_stage: list[str]
    has_yard: bool
    role: str


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


@router.get("/profile/{user_id}")
@router.get("/profile/{user_id}/")
def get_user_profile_data(user_id: str, db: Session = Depends(get_database_session)):
    user = (
        db.query(User).filter((User.id == user_id) | (User.username == user_id)).first()
    )

    if not user:
        new_mock_user = User(
            id=user_id,
            username=user_id,
            name="Usuario Evaluador",
            role="standard",
            size_preference="medium",
            energy_preference="high",
            stage_preference="adult",
            has_yard=False,
        )
        db.add(new_mock_user)
        db.commit()
        db.refresh(new_mock_user)
        user = new_mock_user

    raw_size = getattr(user, "size_preference", "") or ""
    raw_energy = getattr(user, "energy_preference", "") or ""
    raw_stage = getattr(user, "stage_preference", "") or ""

    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "preferences": {
            "size": [s.strip() for s in raw_size.split(",") if s.strip()],
            "energy_level": [e.strip() for e in raw_energy.split(",") if e.strip()],
            "life_stage": [l.strip() for l in raw_stage.split(",") if l.strip()],
            "has_yard": bool(user.has_yard),
        },
    }


@router.post("/profile/{user_id}/preferences")
@router.post("/profile/{user_id}/preferences/")
def update_user_profile_preferences(
    user_id: str,
    payload: UserPreferencesSchema,
    db: Session = Depends(get_database_session),
):
    user = (
        db.query(User).filter((User.id == user_id) | (User.username == user_id)).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User record missing",
        )

    setattr(user, "role", payload.role)
    setattr(user, "size_preference", ",".join(payload.size))
    setattr(user, "energy_preference", ",".join(payload.energy_level))
    setattr(user, "stage_preference", ",".join(payload.life_stage))
    setattr(user, "has_yard", payload.has_yard)

    db.commit()
    return {
        "status": "success",
        "message": "Preferences updated successfully",
    }
