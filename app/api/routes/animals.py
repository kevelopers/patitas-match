from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.animal import Animal
from app.models.user import User
from app.schemas.animal import AnimalCreate, AnimalResponse
from typing import List

router = APIRouter(prefix="/animals", tags=["Animals"])


@router.post("/foundation/{foundation_id}", response_model=AnimalResponse)
def register_animal(
    foundation_id: str, animal: AnimalCreate, db: Session = Depends(get_db)
):
    foundation = (
        db.query(User)
        .filter(User.id == foundation_id, User.role == "foundation")
        .first()
    )
    if not foundation:
        raise HTTPException(status_code=404, detail="Foundation not found")

    new_animal = Animal(
        foundation_id=foundation_id,
        name=animal.name,
        animal_type=animal.animal_type,
        size=animal.size,
        energy_level=animal.energy_level,
        status=animal.status,
    )
    db.add(new_animal)
    db.commit()
    db.refresh(new_animal)
    return new_animal


@router.get("/", response_model=List[AnimalResponse])
def fetch_available_animals(db: Session = Depends(get_db)):
    return db.query(Animal).filter(Animal.status == "available").all()
