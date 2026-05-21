import os
import shutil
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.rescue import RescueReport

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_dynamic_time_ago(created_at: Any) -> str:
    if created_at is None:
        return "Reciente"

    if not isinstance(created_at, datetime):
        return "Reciente"

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    duration = now - created_at
    total_seconds = duration.total_seconds()

    if total_seconds < 60:
        return "Hace un momento"

    total_minutes = total_seconds // 60
    if total_minutes < 60:
        return f"Hace {int(total_minutes)} min"

    total_hours = total_minutes // 60
    if total_hours < 24:
        return f"Hace {int(total_hours)} horas"

    return created_at.strftime("%d/%m/%Y")


@router.get("/rescues")
@router.get("/rescues/")
def get_all_active_rescue_reports(db: Session = Depends(get_database_session)):
    reports = db.query(RescueReport).order_by(RescueReport.id.desc()).all()
    feed_items = []

    for report in reports:
        location_data = str(report.location) if report.location is not None else ""
        location_tokens = location_data.split(" | ")

        display_location = (
            location_tokens[0]
            if len(location_tokens) > 0 and location_tokens[0] != ""
            else "Ubicación desconocida"
        )
        display_description = location_tokens[1] if len(location_tokens) > 1 else ""

        raw_tags = str(report.ai_tags) if report.ai_tags is not None else "alerta"
        processed_tags = [
            tag.strip().lower() for tag in raw_tags.split(",") if tag.strip()
        ]

        reporter_user = report.reporter
        author_name = (
            reporter_user.name
            if reporter_user is not None
            else f"Usuario #{report.reporter_id}"
        )
        author_avatar = (
            "🏥"
            if reporter_user is not None and reporter_user.role == "foundation"
            else "👤"
        )

        saved_path = str(report.image_url) if report.image_url is not None else ""
        final_image_url = (
            f"http://localhost:8000{saved_path}"
            if saved_path.startswith("/static")
            else saved_path
        )

        feed_items.append(
            {
                "id": f"report_{report.id}",
                "authorName": author_name,
                "authorAvatar": author_avatar,
                "location": display_location,
                "timeAgo": calculate_dynamic_time_ago(report.created_at),
                "imageUrl": final_image_url
                or "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&q=80&w=800",
                "description": display_description,
                "tags": processed_tags,
                "status": "pending",
                "likeCount": (
                    report.likes_count if report.likes_count is not None else 0
                ),
            }
        )

    return feed_items


@router.post("/rescues")
@router.post("/rescues/")
def create_rescue_report(
    reporter_id: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_database_session),
):
    text_to_analyze = location.lower()
    file_name_to_analyze = image.filename.lower() if image.filename else ""

    allowed_animals = {
        "perro",
        "perrito",
        "can",
        "canino",
        "dog",
        "puppy",
        "gato",
        "gatito",
        "felino",
        "cat",
        "kitten",
        "pájaro",
        "ave",
        "conejo",
        "mascota",
    }
    forbidden_keywords = {
        "humano",
        "persona",
        "hombre",
        "mujer",
        "niño",
        "ficticio",
        "dragón",
        "unicornio",
    }

    has_valid_animal = any(
        animal in text_to_analyze or animal in file_name_to_analyze
        for animal in allowed_animals
    )
    has_forbidden_content = any(
        forbidden in text_to_analyze or forbidden in file_name_to_analyze
        for forbidden in forbidden_keywords
    )

    if not has_valid_animal or has_forbidden_content:
        return {"status": "rejected", "id": None, "ai_tags": "INVALID_CONTENT"}

    mock_ai_tags = "perro, callejero, resguardado"
    if (
        "gato" in text_to_analyze
        or "gatito" in text_to_analyze
        or "cat" in text_to_analyze
    ):
        mock_ai_tags = "gato, rescate_activo"
    elif "asustado" in text_to_analyze:
        mock_ai_tags = "perro, pequeño, asustado"
    elif "recuperación" in text_to_analyze:
        mock_ai_tags = "perro, recuperación, refugio"

    unique_filename = f"{int(datetime.now().timestamp())}_{image.filename}"
    file_relative_path = f"/{UPLOAD_DIR}/{unique_filename}"
    file_absolute_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_absolute_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    finally:
        image.file.close()

    new_report = RescueReport(
        reporter_id=reporter_id,
        location=location,
        ai_tags=mock_ai_tags,
        image_url=file_relative_path,
        likes_count=0,
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "status": "created",
        "id": new_report.id,
        "ai_tags": mock_ai_tags,
    }
