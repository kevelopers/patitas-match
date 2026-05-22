import os
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.animal import Animal
from app.models.rescue import RescueReport

logging.basicConfig(level=logging.INFO, format="%(message)s")


def reset_database_schema() -> None:
    db_path = "./patitas_match.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    Base.metadata.create_all(bind=engine)


def insert_user_records(db: Session) -> None:
    standard_user = User(
        id="user_tester_2026",
        username="user_tester_2026",
        role="standard",
        name="Usuario Evaluador",
        phone="555-0002",
        size_preference="medium",
        energy_preference="high",
        stage_preference="adult",
        has_yard=True,
    )

    rescuer_user = User(
        id="rescuer_tester_2026",
        username="rescuer_tester_2026",
        role="rescuer",
        name="Rescatista Independiente",
        phone="555-0003",
        size_preference="small",
        energy_preference="medium",
        stage_preference="puppy",
        has_yard=False,
    )

    foundation_user = User(
        id="foundation_01",
        username="foundation_tester_2026",
        role="foundation",
        name="Refugio Esperanza",
        phone="555-0001",
        size_preference="large",
        energy_preference="low",
        stage_preference="senior",
        has_yard=True,
    )

    db.add(standard_user)
    db.add(rescuer_user)
    db.add(foundation_user)

    standard_preferences = UserPreference(
        user_id="user_tester_2026",
        preferred_size=["medium", "large"],
        preferred_energy=["high", "medium"],
        preferred_age=["adult", "puppy"],
        has_yard=True,
    )
    db.add(standard_preferences)


def insert_animal_records(db: Session) -> None:
    foundation_id = "foundation_01"
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


def insert_rescue_records(db: Session) -> None:
    user_id = "user_tester_2026"
    reports = [
        RescueReport(
            reporter_id=user_id,
            location="Sabana Grande | Perrito asustado cerca del bulevar. Parece tener collar pero no veo placa de identificación.",
            ai_tags="perro, pequeño, asustado",
            status="pending",
        ),
        RescueReport(
            reporter_id=user_id,
            location="Bello Monte | Gatito atrapado, los bomberos ya vienen en camino.",
            ai_tags="gato, rescateActivo",
            status="pending",
        ),
        RescueReport(
            reporter_id=user_id,
            location="La Candelaria | Encontramos a este perrito vagando por la plaza. Ya está a salvo en el refugio esperando a sus dueños.",
            ai_tags="perro, mediano, aSalvo",
            status="pending",
        ),
        RescueReport(
            reporter_id=user_id,
            location="La Florida | Actualización del caso de ayer: Rocky está recuperándose súper bien. Pronto estará listo para adopción.",
            ai_tags="perro, recuperación, refugio",
            status="pending",
        ),
    ]
    db.add_all(reports)


def execute_seeding_process() -> None:
    reset_database_schema()
    db = SessionLocal()
    try:
        insert_user_records(db)
        insert_animal_records(db)
        insert_rescue_records(db)
        db.commit()
    except Exception as error:
        db.rollback()
        raise error
    finally:
        db.close()


if __name__ == "__main__":
    execute_seeding_process()
