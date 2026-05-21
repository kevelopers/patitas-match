from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.match_service import get_user_match_stack
from app.models.match import Match, Rejection

router = APIRouter()


class MatchCreationPayload(BaseModel):
    user_id: str
    animal_id: int


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}/stack")
def retrieve_match_stack(user_id: str, db: Session = Depends(get_database_session)):
    return get_user_match_stack(db, user_id)


@router.post("")
def persist_user_match(
    payload: MatchCreationPayload, db: Session = Depends(get_database_session)
):
    duplicated_match = (
        db.query(Match)
        .filter(Match.user_id == payload.user_id, Match.animal_id == payload.animal_id)
        .first()
    )

    if duplicated_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match relation already recorded for this resource",
        )

    new_match = Match(user_id=payload.user_id, animal_id=payload.animal_id)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return {"status": "persisted", "id": new_match.id}


@router.post("/reject")
def persist_user_rejection(
    payload: MatchCreationPayload, db: Session = Depends(get_database_session)
):
    duplicated_rejection = (
        db.query(Rejection)
        .filter(
            Rejection.user_id == payload.user_id,
            Rejection.animal_id == payload.animal_id,
        )
        .first()
    )

    if duplicated_rejection:
        return {"status": "already_rejected"}

    new_rejection = Rejection(user_id=payload.user_id, animal_id=payload.animal_id)
    db.add(new_rejection)
    db.commit()
    return {"status": "rejected"}
