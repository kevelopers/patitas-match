import os
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.animal import Animal, AnimalFollowUpLog
from app.models.rescue import RescueReport, RescueLike
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(message)s")


def reset_database_schema() -> None:
    db_path = "./patitas_match.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    Base.metadata.create_all(bind=engine)


def insert_user_records(db: Session) -> None:
    default_hashed_password = get_password_hash("123")

    standard_user = User(
        id="user_tester_2026",
        username="tester",
        hashed_password=default_hashed_password,
        role="standard",
        name="Usuario Evaluador",
        phone="584125551122",
        size_preference="medium",
        energy_preference="high",
        stage_preference="adult",
        has_yard=True,
    )

    rescuer_user = User(
        id="rescuer_tester_2026",
        username="rescuer",
        hashed_password=default_hashed_password,
        role="rescuer",
        name="Rescatista Independiente",
        phone="584145553344",
        size_preference="small",
        energy_preference="medium",
        stage_preference="young",
        has_yard=False,
    )

    foundation_user = User(
        id="foundation_01",
        username="foundation",
        hashed_password=default_hashed_password,
        role="foundation",
        name="Refugio Esperanza",
        phone="584125799911",
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
        preferred_size=["medium"],
        preferred_energy=["high"],
        preferred_age=["adult"],
        has_yard=True,
    )
    db.add(standard_preferences)


def insert_animal_records(db: Session) -> None:
    foundation_id = "foundation_01"

    animal_draft = Animal(
        foundation_id=foundation_id,
        name="Simba",
        animal_type="Perro",
        size="small",
        energy_level="high",
        age="young",
        status="draft",
        description="Cachorro recién ingresado, actualmente en evaluación médica intermedia.",
    )

    animal_max = Animal(
        foundation_id=foundation_id,
        name="Max",
        animal_type="Perro",
        size="medium",
        energy_level="high",
        age="adult",
        status="available",
        description="Muy amigable, le encanta correr en espacios abiertos.",
    )

    animal_bella = Animal(
        foundation_id=foundation_id,
        name="Bella",
        animal_type="Perro",
        size="small",
        energy_level="low",
        age="young",
        status="available",
        description="Tranquila, ideal para apartamentos y familias.",
    )

    animal_rocky = Animal(
        foundation_id=foundation_id,
        name="Rocky",
        animal_type="Perro",
        size="large",
        energy_level="high",
        age="adult",
        status="in_progress",
        description="Excelente guardián, requiere entrenamiento constante.",
    )

    animal_kira = Animal(
        foundation_id=foundation_id,
        name="Kira",
        animal_type="Perro",
        size="medium",
        energy_level="low",
        age="senior",
        status="adopted",
        description="Rescatada de la calle, muy agradecida y silenciosa.",
    )

    animal_toby = Animal(
        foundation_id=foundation_id,
        name="Toby",
        animal_type="Perro",
        size="medium",
        energy_level="medium",
        age="young",
        status="available",
        description="Juguetón, le gusta socializar con otros perritos y niños.",
    )

    animal_loki = Animal(
        foundation_id=foundation_id,
        name="Loki",
        animal_type="Perro",
        size="small",
        energy_level="low",
        age="senior",
        status="available",
        description="Perrito senior que busca paz. Tiene índice bajo, al deslizar a la derecha fallará el match por baja afinidad.",
    )

    db.add_all(
        [
            animal_draft,
            animal_max,
            animal_bella,
            animal_rocky,
            animal_kira,
            animal_toby,
            animal_loki,
        ]
    )
    db.flush()

    log_entry = AnimalFollowUpLog(
        animal_id=animal_kira.id,
        title="Control de 1 Mes",
        text="Adoptante envió fotos. Adaptación de la mascota exitosa en casa, buena convivencia.",
    )
    db.add(log_entry)


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
            ai_tags="gato, enRescate",
            status="in_progress",
        ),
        RescueReport(
            reporter_id=user_id,
            location="La Candelaria | Encontramos a este perrito vagando por la plaza. Ya está a salvo en el refugio esperando a sus dueños.",
            ai_tags="perro, mediano, resguardado",
            status="rescued",
        ),
        RescueReport(
            reporter_id=user_id,
            location="La Florida | Alerta de campo solventada. El animal fue trasladado a las instalaciones del aliado.",
            ai_tags="perro, recuperado, enRefugio",
            status="in_shelter",
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
