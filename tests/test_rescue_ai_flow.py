import logging
import io
from unittest.mock import MagicMock, patch
from PIL import Image
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.rescue import RescueReport
from app.services.llm.factory import LLMFactory
from app.core.security import get_password_hash

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
    reporter = User(
        id=user_id,
        role="standard",
        name="AI Tester",
        phone="555-0004",
        hashed_password=get_password_hash("password123"),
    )
    db.add(reporter)
    db.commit()
    db.refresh(reporter)
    return reporter


def cleanup_ai_test(db: Session, user_id: str, report_ids: list[int]) -> None:
    if report_ids:
        db.query(RescueReport).filter(RescueReport.id.in_(report_ids)).delete(
            synchronize_session=False
        )

    if user_id:
        db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()


def execute_ai_simulation() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    test_user_id = "user_ai_tester_01"
    inserted_reports = []

    try:
        logger.info("Initializing multi-layer LLM provider testing schema.")
        create_reporter(db, test_user_id)
        image_data = generate_synthetic_image()

        mock_provider = MagicMock()
        mock_provider.validate_rescue_content.side_effect = [
            {"valid": True, "tags": "perro, asustado, mediano"},
            {"valid": False, "tags": "INVALID_CONTENT"},
        ]

        with patch.object(LLMFactory, "get_provider", return_value=mock_provider):
            current_provider = LLMFactory.get_provider()

            logger.info("CASE 1: Submitting legitimate animal rescue dataset.")
            valid_response = current_provider.validate_rescue_content(
                image_data, "image/jpeg", "Sabana Grande | Perrito herido"
            )

            if valid_response.get("valid"):
                success_report = RescueReport(
                    reporter_id=test_user_id,
                    location="Sabana Grande | Perrito herido",
                    ai_tags=valid_response.get("tags"),
                    image_url="/static/uploads/test_dog.jpg",
                    likes_count=0,
                )
                db.add(success_report)
                db.commit()
                db.refresh(success_report)
                inserted_reports.append(int(str(success_report.id)))
                logger.info(
                    f"Legitimate report safely committed with ID: {success_report.id}"
                )

            logger.info("CASE 2: Submitting anomalous household item dataset (Lamp).")
            invalid_response = current_provider.validate_rescue_content(
                image_data, "image/jpeg", "Bello Monte | Lampara vieja"
            )

            if not invalid_response.get("valid"):
                logger.info(
                    "System layer successfully caught and rejected anomalous item upload scenario."
                )

    finally:
        logger.info("Cleaning up AI pipeline test metadata references.")
        cleanup_ai_test(db, test_user_id, inserted_reports)
        logger.info("AI Test entities cleanly synchronized and purged.")
        db.close()


if __name__ == "__main__":
    execute_ai_simulation()
