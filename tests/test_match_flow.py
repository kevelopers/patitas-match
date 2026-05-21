import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.animal import Animal
from app.models.match import Match, Rejection
from app.services.match_service import get_user_match_stack

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
            age="adult",
            status="available",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Luna",
            animal_type="dog",
            size="small",
            energy_level="low",
            age="puppy",
            status="available",
        ),
        Animal(
            foundation_id=foundation_id,
            name="Apollo",
            animal_type="dog",
            size="medium",
            energy_level="high",
            age="adult",
            status="available",
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
    db: Session, user_id: str, sizes: list, energies: list, ages: list, yard: bool
) -> UserPreference:
    preference = UserPreference(
        user_id=user_id,
        preferred_size=sizes,
        preferred_energy=energies,
        preferred_age=ages,
        has_yard=yard,
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def clean_up_data(db: Session, user_ids: list[str], animal_ids: list[int]) -> None:
    if animal_ids:
        db.query(Match).filter(Match.animal_id.in_(animal_ids)).delete(
            synchronize_session=False
        )
        db.query(Rejection).filter(Rejection.animal_id.in_(animal_ids)).delete(
            synchronize_session=False
        )
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
        logger.info("Initializing comprehensive match test routing.")

        f_id = "foundation_hope_01"
        create_foundation(db, f_id)
        inserted_users.append(f_id)

        animals = create_animals(db, f_id)
        inserted_animals.extend([int(str(a.id)) for a in animals])

        tester_id = "user_jane_doe"
        create_adopter(db, tester_id, "Jane Doe", "555-0002")
        inserted_users.append(tester_id)
        create_preference(
            db,
            tester_id,
            ["small", "medium"],
            ["low", "high"],
            ["puppy", "adult"],
            False,
        )

        logger.info("CASE 1: Requesting base configuration stack matching preferences.")
        initial_stack = get_user_match_stack(db, tester_id)
        logger.info(f"Total entries fetched: {len(initial_stack)}")

        target_match_animal_id = initial_stack[0]["id"]
        logger.info(
            f"CASE 2: Persisting positive connection interaction (Match) for animal ID: {target_match_animal_id}"
        )
        simulated_match = Match(user_id=tester_id, animal_id=target_match_animal_id)
        db.add(simulated_match)
        db.commit()

        post_match_stack = get_user_match_stack(db, tester_id)
        logger.info(
            f"Remaining entries after match constraint: {len(post_match_stack)}"
        )

        target_reject_animal_id = post_match_stack[0]["id"]
        logger.info(
            f"CASE 3: Persisting negative skip interaction (Rejection) for animal ID: {target_reject_animal_id}"
        )
        simulated_rejection = Rejection(
            user_id=tester_id, animal_id=target_reject_animal_id
        )
        db.add(simulated_rejection)
        db.commit()

        final_stack = get_user_match_stack(db, tester_id)
        logger.info(f"Final pipeline stack entries remaining: {len(final_stack)}")

    finally:
        logger.info("Initiating database cleanup routine.")
        clean_up_data(db, inserted_users, inserted_animals)
        logger.info("Cleanup complete. Test entities safely purged.")
        db.close()


if __name__ == "__main__":
    execute_simulation()
