import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.animal import Animal
from app.services.match_service import build_match_stack

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_foundation(db: Session, user_id: str) -> User:
    foundation = User(
        id=user_id, role="foundation", name="Hope Shelter", phone="555-0001"
    )
    db.add(foundation)
    db.commit()
    db.refresh(foundation)
    return foundation


def create_animals(db: Session, foundation_id: str) -> list[Animal]:
    animals = [
        Animal(
            foundation_id=foundation_id,
            name="Titan",
            animal_type="dog",
            size="large",
            energy_level="high",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Luna",
            animal_type="dog",
            size="small",
            energy_level="low",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Apollo",
            animal_type="dog",
            size="medium",
            energy_level="high",
        ),
    ]
    db.add_all(animals)
    db.commit()
    for animal in animals:
        db.refresh(animal)
    return animals


def create_adopter(db: Session, user_id: str, name: str, phone: str) -> User:
    adopter = User(id=user_id, role="standard", name=name, phone=phone)
    db.add(adopter)
    db.commit()
    db.refresh(adopter)
    return adopter


def create_preference(
    db: Session, user_id: str, size: str, energy: str, yard: bool
) -> UserPreference:
    preference = UserPreference(
        user_id=user_id, preferred_size=size, preferred_energy=energy, has_yard=yard
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def clean_up_data(db: Session, user_ids: list[str], animal_ids: list[int]) -> None:
    if animal_ids:
        db.query(Animal).filter(Animal.id.in_(animal_ids)).delete(
            synchronize_session=False
        )

    if user_ids:
        db.query(UserPreference).filter(UserPreference.user_id.in_(user_ids)).delete(
            synchronize_session=False
        )
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)

    db.commit()


def execute_simulation() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted_users = []
    inserted_animals = []

    try:
        logger.info("Initializing test data injection.")

        f_id = "foundation_hope_01"
        create_foundation(db, f_id)
        inserted_users.append(f_id)

        animals = create_animals(db, f_id)
        inserted_animals.extend([int(str(a.id)) for a in animals])

        a_match_id = "user_jane_doe"
        create_adopter(db, a_match_id, "Jane Doe", "555-0002")
        inserted_users.append(a_match_id)
        create_preference(db, a_match_id, "small", "low", False)

        a_no_match_id = "user_john_smith"
        create_adopter(db, a_no_match_id, "John Smith", "555-0003")
        inserted_users.append(a_no_match_id)
        create_preference(db, a_no_match_id, "giant", "lazy", False)

        logger.info("--- STARTING CASE 1: MATCH SCENARIO ---")
        matches = build_match_stack(db, a_match_id)
        logger.info(f"Total matches found for {a_match_id}: {len(matches)}")
        for match in matches:
            logger.info(
                f"MATCH DATA | Name: {match['name']} | Score: {match['match_score']}"
            )

        logger.info("--- STARTING CASE 2: NO MATCH SCENARIO ---")
        no_matches = build_match_stack(db, a_no_match_id)
        logger.info(f"Total matches found for {a_no_match_id}: {len(no_matches)}")
        if not no_matches:
            logger.info("System correctly filtered out all incompatible animals.")

    finally:
        logger.info("Initiating database cleanup routine.")
        clean_up_data(db, inserted_users, inserted_animals)
        logger.info("Cleanup complete. Test entities safely purged.")
        db.close()


if __name__ == "__main__":
    execute_simulation()
