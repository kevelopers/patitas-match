import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import SessionLocal
from app.models.animal import Animal, AnimalFollowUpLog
from app.models.match import Match

router = APIRouter(prefix="/animals", tags=["Animals"])

PROFILE_UPLOAD_DIR = "static/uploads/animal_profiles"
os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_profile_picture_stream(image_file: UploadFile) -> str:
    timestamp_prefix = int(datetime.now().timestamp())
    sanitized_filename = f"{timestamp_prefix}_{image_file.filename}"
    file_relative_path = f"/{PROFILE_UPLOAD_DIR}/{sanitized_filename}"
    file_absolute_path = os.path.join(PROFILE_UPLOAD_DIR, sanitized_filename)

    with open(file_absolute_path, "wb") as storage_buffer:
        shutil.copyfileobj(image_file.file, storage_buffer)

    return file_relative_path


@router.get("/foundation/{foundation_id}")
@router.get("/foundation/{foundation_id}/")
def get_foundation_animals(
    foundation_id: str, db: Session = Depends(get_database_session)
):
    animals = (
        db.query(Animal)
        .filter(Animal.foundation_id == foundation_id)
        .order_by(Animal.id.desc())
        .all()
    )
    result = []

    for animal in animals:
        matches_count = db.query(Match).filter(Match.animal_id == animal.id).count()
        logs = (
            db.query(AnimalFollowUpLog)
            .filter(AnimalFollowUpLog.animal_id == animal.id)
            .order_by(AnimalFollowUpLog.id.desc())
            .all()
        )

        saved_path = str(animal.image_url) if animal.image_url is not None else ""
        final_photo_url = f"http://localhost:8000{saved_path}" if saved_path else "🐾"

        result.append(
            {
                "id": animal.id,
                "name": animal.name,
                "type": animal.animal_type,
                "size": animal.size,
                "energyLevel": animal.energy_level,
                "age": animal.age,
                "status": animal.status,
                "description": animal.description or "",
                "matchesCount": matches_count,
                "photo": final_photo_url,
                "followUpLogs": [
                    {
                        "id": log.id,
                        "title": log.title,
                        "text": log.text,
                        "date": log.created_at.strftime("%d/%m/%Y"),
                    }
                    for log in logs
                ],
            }
        )

    return result


@router.get("/discovery/{user_id}")
@router.get("/discovery/{user_id}/")
def get_discovery_cards(user_id: str, db: Session = Depends(get_database_session)):
    available_animals = db.query(Animal).filter(Animal.status == "available").all()
    cards = []

    for animal in available_animals:
        saved_path = str(animal.image_url) if animal.image_url is not None else ""
        final_photo_url = f"http://localhost:8000{saved_path}" if saved_path else "🐾"

        cards.append(
            {
                "id": animal.id,
                "name": animal.name,
                "type": animal.animal_type,
                "size": animal.size,
                "energy_level": animal.energy_level,
                "age": animal.age,
                "description": animal.description or "",
                "photo": final_photo_url,
                "match_score": 100,
            }
        )

    return cards


@router.post("")
@router.post("/")
def create_animal_profile(
    foundation_id: str = Form(...),
    name: str = Form(...),
    animal_type: str = Form(...),
    size: str = Form(...),
    energy_level: str = Form(...),
    age: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("available"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_database_session),
):
    saved_image_path = None
    if image:
        saved_image_path = save_profile_picture_stream(image)

    new_animal = Animal(
        foundation_id=foundation_id,
        name=name,
        animal_type=animal_type,
        size=size,
        energy_level=energy_level,
        age=age,
        description=description,
        status=status,
        image_url=saved_image_path,
    )
    db.add(new_animal)
    db.commit()
    db.refresh(new_animal)
    return {"status": "success", "id": new_animal.id}


@router.post("/{animal_id}/update")
@router.post("/{animal_id}/update/")
def update_animal_profile(
    animal_id: int,
    name: str = Form(...),
    animal_type: str = Form(...),
    size: str = Form(...),
    energy_level: str = Form(...),
    age: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_database_session),
):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    setattr(animal, "name", name)
    setattr(animal, "animal_type", animal_type)
    setattr(animal, "size", size)
    setattr(animal, "energy_level", energy_level)
    setattr(animal, "age", age)
    setattr(animal, "description", description)
    setattr(animal, "status", status)

    if image:
        saved_image_path = save_profile_picture_stream(image)
        setattr(animal, "image_url", saved_image_path)

    db.commit()
    return {"status": "success"}


@router.post("/{animal_id}/match")
@router.post("/{animal_id}/match/")
def register_animal_match(animal_id: int, db: Session = Depends(get_database_session)):
    user_id = "user_tester_2026"
    existing_match = (
        db.query(Match)
        .filter(Match.user_id == user_id, Match.animal_id == animal_id)
        .first()
    )

    if not existing_match:
        new_match = Match(user_id=user_id, animal_id=animal_id)
        db.add(new_match)
        db.commit()

    return {"status": "success"}


@router.post("/{animal_id}/logs")
@router.post("/{animal_id}/logs/")
def add_animal_follow_up_log(
    animal_id: int,
    title: str = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_database_session),
):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    new_log = AnimalFollowUpLog(animal_id=animal_id, title=title, text=text)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "id": new_log.id,
        "title": new_log.title,
        "text": new_log.text,
        "date": new_log.created_at.strftime("%d/%m/%Y"),
    }
