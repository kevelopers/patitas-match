import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Any
from datetime import datetime
from app.db.database import SessionLocal
from app.models.animal import Animal, AnimalFollowUpLog
from app.models.match import Match, Rejection
from app.models.user import User

router = APIRouter(prefix="/animals", tags=["Animals"])

PROFILE_UPLOAD_DIR = "static/uploads/animal_profiles"
os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_absolute_url_path(relative_path: Any) -> str:
    if relative_path is None:
        return "🐾"
    sanitized = str(relative_path).lstrip("/")
    return f"http://localhost:8000/{sanitized}"


def save_profile_picture_stream(image_file: UploadFile) -> str:
    timestamp_prefix = int(datetime.now().timestamp())
    sanitized_filename = f"{timestamp_prefix}_{image_file.filename}"
    file_relative_path = f"/{PROFILE_UPLOAD_DIR}/{sanitized_filename}"
    file_absolute_path = os.path.join(PROFILE_UPLOAD_DIR, sanitized_filename)

    with open(file_absolute_path, "wb") as storage_buffer:
        shutil.copyfileobj(image_file.file, storage_buffer)

    return file_relative_path


def calculate_animal_affinity_score(user: User, animal: Animal) -> int:
    score = 0

    user_sizes = [
        s.strip().lower() for s in (user.size_preference or "").split(",") if s.strip()
    ]
    user_energies = [
        e.strip().lower()
        for e in (user.energy_preference or "").split(",")
        if e.strip()
    ]
    user_stages = [
        l.strip().lower() for l in (user.stage_preference or "").split(",") if l.strip()
    ]

    if str(animal.size).lower() in user_sizes:
        score += 33
    if str(animal.energy_level).lower() in user_energies:
        score += 33
    if str(animal.age).lower() in user_stages:
        score += 34

    return score


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

        saved_path = str(animal.image_url) if animal.image_url is not None else None

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
                "photo": clean_absolute_url_path(saved_path),
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
    user = (
        db.query(User).filter((User.id == user_id) | (User.username == user_id)).first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    matched_ids = [
        m[0] for m in db.query(Match.animal_id).filter(Match.user_id == user.id).all()
    ]
    rejected_ids = [
        r[0]
        for r in db.query(Rejection.animal_id)
        .filter(Rejection.user_id == user.id)
        .all()
    ]
    excluded_ids = set(matched_ids + rejected_ids)

    query = db.query(Animal).filter(Animal.status == "available")
    if len(excluded_ids) > 0:
        query = query.filter(~Animal.id.in_(list(excluded_ids)))

    available_animals = query.all()
    cards = []

    for animal in available_animals:
        saved_path = str(animal.image_url) if animal.image_url is not None else None
        affinity = calculate_animal_affinity_score(user, animal)

        cards.append(
            {
                "id": animal.id,
                "name": animal.name,
                "type": animal.animal_type,
                "size": animal.size,
                "energy_level": animal.energy_level,
                "age": animal.age,
                "description": animal.description or "",
                "photo": clean_absolute_url_path(saved_path),
                "match_score": affinity,
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
    status: str = Form("draft"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_database_session),
):
    saved_image_path = None
    if image is not None:
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
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    setattr(animal, "name", name)
    setattr(animal, "animal_type", animal_type)
    setattr(animal, "size", size)
    setattr(animal, "energy_level", energy_level)
    setattr(animal, "age", age)
    setattr(animal, "description", description)
    setattr(animal, "status", status)

    if image is not None:
        saved_image_path = save_profile_picture_stream(image)
        setattr(animal, "image_url", saved_image_path)

    db.commit()
    return {"status": "success"}


@router.post("/{animal_id}/match")
@router.post("/{animal_id}/match/")
def register_animal_match(
    animal_id: int,
    user_id: str = "user_tester_2026",
    db: Session = Depends(get_database_session),
):
    user = (
        db.query(User).filter((User.id == user_id) | (User.username == user_id)).first()
    )
    animal = db.query(Animal).filter(Animal.id == animal_id).first()

    if user is None or animal is None:
        raise HTTPException(status_code=404, detail="Records missing")

    affinity = calculate_animal_affinity_score(user, animal)

    if affinity < 60:
        existing_reject = (
            db.query(Rejection)
            .filter(Rejection.user_id == user.id, Rejection.animal_id == animal_id)
            .first()
        )
        if existing_reject is None:
            new_rejection = Rejection(user_id=user.id, animal_id=animal_id)
            db.add(new_rejection)
            db.commit()
        return {"status": "low_affinity", "phone": None}

    existing_match = (
        db.query(Match)
        .filter(Match.user_id == user.id, Match.animal_id == animal_id)
        .first()
    )

    if existing_match is None:
        new_match = Match(user_id=user.id, animal_id=animal_id)
        db.add(new_match)
        db.commit()

    foundation_phone = "584125799911"
    owner_foundation = db.query(User).filter(User.id == animal.foundation_id).first()
    if owner_foundation is not None and owner_foundation.phone is not None:
        foundation_phone = str(owner_foundation.phone)

    return {"status": "success", "phone": foundation_phone}


@router.post("/{animal_id}/reject")
@router.post("/{animal_id}/reject/")
def register_animal_rejection(
    animal_id: int,
    user_id: str = "user_tester_2026",
    db: Session = Depends(get_database_session),
):
    user = (
        db.query(User).filter((User.id == user_id) | (User.username == user_id)).first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_reject = (
        db.query(Rejection)
        .filter(Rejection.user_id == user.id, Rejection.animal_id == animal_id)
        .first()
    )

    if existing_reject is None:
        new_reject = Rejection(user_id=user.id, animal_id=animal_id)
        db.add(new_reject)
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
    if animal is None:
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
