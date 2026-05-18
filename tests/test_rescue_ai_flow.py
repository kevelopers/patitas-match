import logging
import io
from PIL import Image
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.rescue import RescueReport
from app.ai.analyzer import process_rescue_image

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_synthetic_image() -> bytes:
    img = Image.new("RGB", (224, 224), color=(205, 133, 63))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


def create_reporter(db: Session, user_id: str) -> User:
    reporter = User(id=user_id, role="standard", name="AI Tester", phone="555-0004")
    db.add(reporter)
    db.commit()
    db.refresh(reporter)
    return reporter


def cleanup_ai_test(db: Session, user_id: str, report_id: int) -> None:
    if report_id:
        db.query(RescueReport).filter(RescueReport.id == report_id).delete(
            synchronize_session=False
        )

    if user_id:
        db.query(User).filter(User.id == user_id).delete(synchronize_session=False)

    db.commit()


def execute_ai_simulation() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    test_user_id = "user_ai_tester_01"
    report_id = None

    try:
        logger.info("Initializing AI test environment.")
        create_reporter(db, test_user_id)

        logger.info("Generating synthetic image byte stream.")
        image_data = generate_synthetic_image()

        logger.info(
            "Triggering AI Vision Model. (Note: Model will download on first execution)"
        )
        ai_tags = process_rescue_image(image_data)
        logger.info(f"AI Analysis Complete. Extracted Tags: [{ai_tags}]")

        logger.info("Simulating database insertion for Rescue Report.")
        new_report = RescueReport(
            reporter_id=test_user_id,
            location="Parque del Este, Caracas",
            ai_tags=ai_tags,
            status="pending",
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        report_id = int(str(new_report.id))
        logger.info(
            f"Database insertion successful. Report ID: {report_id} | Status: {new_report.status}"
        )

    finally:
        logger.info("Cleaning up AI test data.")
        if report_id is not None:
            cleanup_ai_test(db, test_user_id, report_id)
        logger.info("Test entities safely purged. Database clean.")
        db.close()


if __name__ == "__main__":
    execute_ai_simulation()
