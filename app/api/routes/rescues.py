from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.rescue import RescueReport
from app.models.user import User
from app.schemas.rescue import RescueReportResponse
from app.ai.analyzer import process_rescue_image

router = APIRouter(prefix="/rescues", tags=["Rescue Operations"])


@router.post("/", response_model=RescueReportResponse)
def report_rescue(
    reporter_id: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    reporter = db.query(User).filter(User.id == reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")

    image_data = image.file.read()
    ai_generated_tags = process_rescue_image(image_data)

    new_report = RescueReport(
        reporter_id=reporter_id,
        location=location,
        ai_tags=ai_generated_tags,
        status="pending",
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report
