import os
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.animal import Animal
from app.models.rescue import RescueReport
from app.models.match import Match, Rejection

logging.basicConfig(level=logging.INFO, format="%(message)s")


def reset_database_schema() -> None:
    db_path = "./patitas_match.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        logging.info("Physical database file successfully deleted.")

    Base.metadata.create_all(bind=engine)
    logging.info("Schema tables successfully generated.")


def insert_foundation_records(db: Session) -> None:
    foundation_id = "foundation_01"

    foundation = User(
        id=foundation_id, role="foundation", name="Refugio Esperanza", phone="555-0001"
    )
    db.add(foundation)

    animals = [
        Animal(
            foundation_id=foundation_id,
            name="Max",
            animal_type="dog",
            size="medium",
            energy_level="high",
            age="adult",
            status="available",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Bella",
            animal_type="dog",
            size="small",
            energy_level="low",
            age="puppy",
            status="available",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Rocky",
            animal_type="dog",
            size="large",
            energy_level="high",
            age="adult",
            status="available",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Kira",
            animal_type="dog",
            size="medium",
            energy_level="low",
            age="senior",
            status="available",
        ),
    ]
    db.add_all(animals)


def insert_tester_records(db: Session) -> None:
    user_id = "user_tester_2026"

    user = User(id=user_id, role="standard", name="Usuario Evaluador", phone="555-0002")
    db.add(user)

    preferences = UserPreference(
        user_id=user_id,
        preferred_size=["medium", "large"],
        preferred_energy=["high", "medium"],
        preferred_age=["adult", "puppy"],
        has_yard=True,
    )
    db.add(preferences)


def execute_seeding_process() -> None:
    reset_database_schema()
    db = SessionLocal()

    try:
        insert_foundation_records(db)
        insert_tester_records(db)
        db.commit()
        logging.info("Database schema reset and successfully seeded.")
    except Exception as error:
        db.rollback()
        logging.error(f"Seeding process failed: {error}")
        raise error
    finally:
        db.close()


if __name__ == "__main__":
    execute_seeding_process()
