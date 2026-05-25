import os
import shutil
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Request,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.rescue import RescueReport, RescueLike
from app.services.llm.factory import LLMFactory
from app.models.user import User
from app.core.security import get_authenticated_user, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class StatusUpdateSchema(BaseModel):
    status: str
    allied_foundation_id: Optional[str] = None
    external_shelter_details: Optional[str] = None


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
def get_all_active_rescue_reports(
    request: Request, db: Session = Depends(get_database_session)
):
    current_user_id = None
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            current_user_id = payload.get("sub")
        except JWTError:
            pass

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
        processed_tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]

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
            f"http://localhost:8000/{saved_path.lstrip('/')}"
            if saved_path
            else "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop-60&w=800"
        )
        current_status = getattr(report, "status", "pending") or "pending"
        rescuer_id = getattr(report, "rescuer_id", None)

        has_liked = False
        if current_user_id:
            like_exists = (
                db.query(RescueLike)
                .filter(
                    RescueLike.user_id == current_user_id,
                    RescueLike.report_id == report.id,
                )
                .first()
            )
            has_liked = like_exists is not None

        feed_items.append(
            {
                "id": f"report_{report.id}",
                "authorName": author_name,
                "authorAvatar": author_avatar,
                "location": display_location,
                "timeAgo": calculate_dynamic_time_ago(report.created_at),
                "imageUrl": final_image_url,
                "description": display_description,
                "tags": processed_tags,
                "status": current_status,
                "likeCount": (
                    report.likes_count if report.likes_count is not None else 0
                ),
                "hasLiked": has_liked,
                "rescuerId": rescuer_id,
                "urgency": getattr(report, "urgency", "medium"),
                "breedMix": getattr(report, "breed_mix", "Desconocido"),
                "detectedMood": getattr(report, "detected_mood", "Alerta"),
                "physicalCondition": getattr(report, "physical_condition", "Estable"),
                "firstAidAdvice": getattr(report, "first_aid_advice", ""),
            }
        )
    return feed_items


@router.post("/rescues/{report_id}/status")
@router.post("/rescues/{report_id}/status/")
def update_rescue_report_status(
    report_id: int,
    payload: StatusUpdateSchema,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    report = db.query(RescueReport).filter(RescueReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report record missing"
        )

    new_status = payload.status

    if new_status == "in_progress":
        current_status = str(getattr(report, "status", "pending"))
        if current_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este caso ya esta siendo atendido por otro rescatista",
            )
        setattr(report, "rescuer_id", current_user.id)

    setattr(report, "status", new_status)

    if new_status == "in_shelter":
        setattr(report, "allied_foundation_id", payload.allied_foundation_id)
        setattr(report, "external_shelter_details", payload.external_shelter_details)

    raw_tags = str(report.ai_tags) if report.ai_tags is not None else ""
    tags_list = [t.strip() for t in raw_tags.split(",") if t.strip()]

    filtered_tags = [
        t
        for t in tags_list
        if t.lower()
        not in {
            "pendiente",
            "enrescate",
            "rescatado",
            "enrefugio",
            "adoptado",
            "nolocalizado",
        }
    ]

    if new_status == "in_progress":
        filtered_tags.append("enRescate")
    elif new_status == "rescued":
        filtered_tags.append("rescatado")
    elif new_status == "in_shelter":
        filtered_tags.append("enRefugio")
    elif new_status == "adopted":
        filtered_tags.append("adoptado")
    elif new_status == "not_found":
        filtered_tags.append("noLocalizado")

    setattr(report, "ai_tags", ", ".join(filtered_tags))
    db.commit()

    return {
        "status": "success",
        "new_status": new_status,
        "updated_tags": filtered_tags,
    }


@router.post("/rescues")
@router.post("/rescues/")
def create_rescue_report(
    location: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    image_bytes = image.file.read()
    image.file.seek(0)

    mime_type = image.content_type or "image/jpeg"
    llm_provider = LLMFactory.get_provider()
    ai_result = llm_provider.validate_rescue_content(image_bytes, mime_type, location)

    if not ai_result.get("valid", False):
        return {"status": "rejected", "id": None, "ai_tags": "INVALID_CONTENT"}

    chosen_tags = ai_result.get("tags", "perro, callejero")
    unique_filename = f"{int(datetime.now().timestamp())}_{image.filename}"
    file_relative_path = f"/{UPLOAD_DIR}/{unique_filename}"
    file_absolute_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_absolute_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    finally:
        image.file.close()

    new_report = RescueReport(
        reporter_id=current_user.id,
        location=location,
        image_url=file_relative_path,
        ai_tags=chosen_tags,
        likes_count=0,
        status="pending",
        urgency=ai_result.get("urgency", "medium"),
        breed_mix=ai_result.get("breed_mix", "Mezcla Desconocida"),
        detected_mood=ai_result.get("detected_mood", "Alerta"),
        physical_condition=ai_result.get("physical_condition", "Estable"),
        first_aid_advice=ai_result.get(
            "first_aid_advice",
            "Mantener distancia segura, no acorralar al animal y proveer agua limpia de ser posible.",
        ),
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return {"status": "created", "id": new_report.id, "ai_tags": chosen_tags}


@router.post("/rescues/{report_id}/like")
@router.post("/rescues/{report_id}/like/")
def register_rescue_report_like(
    report_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    report = db.query(RescueReport).filter(RescueReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report record missing")

    existing_like = (
        db.query(RescueLike)
        .filter(
            RescueLike.user_id == current_user.id, RescueLike.report_id == report_id
        )
        .first()
    )

    if not existing_like:
        new_like = RescueLike(user_id=current_user.id, report_id=report_id)
        db.add(new_like)
        raw_likes = getattr(report, "likes_count", 0)
        current_likes = int(raw_likes) if raw_likes is not None else 0
        setattr(report, "likes_count", current_likes + 1)
        db.commit()

    return {"status": "success", "likes_count": report.likes_count}


@router.post("/rescues/{report_id}/unlike")
@router.post("/rescues/{report_id}/unlike/")
def register_rescue_report_unlike(
    report_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_authenticated_user),
):
    report = db.query(RescueReport).filter(RescueReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report record missing")

    existing_like = (
        db.query(RescueLike)
        .filter(
            RescueLike.user_id == current_user.id, RescueLike.report_id == report_id
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        raw_likes = getattr(report, "likes_count", 0)
        current_likes = int(raw_likes) if raw_likes is not None else 0
        setattr(report, "likes_count", max(0, current_likes - 1))
        db.commit()

    return {"status": "success", "likes_count": report.likes_count}
