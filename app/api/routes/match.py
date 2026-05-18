from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.match_service import build_match_stack
from typing import List, Dict, Any

router = APIRouter(prefix="/matches", tags=["Match System"])


@router.get("/{user_id}/stack", response_model=List[Dict[str, Any]])
def get_user_match_stack(user_id: str, db: Session = Depends(get_db)):
    match_stack = build_match_stack(db, user_id)
    if not match_stack:
        raise HTTPException(
            status_code=404, detail="No matches found or missing user preferences"
        )
    return match_stack
