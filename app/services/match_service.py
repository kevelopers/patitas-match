from sqlalchemy.orm import Session
from app.models.user import UserPreference
from app.models.animal import Animal
from typing import List, Dict, Any, Optional


def get_user_preferences(db: Session, user_id: str) -> Optional[UserPreference]:
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()


def fetch_candidate_animals(db: Session) -> List[Animal]:
    return db.query(Animal).filter(Animal.status == "available").all()


def calculate_score(preference: UserPreference, animal: Animal) -> int:
    score = 0
    pref_size = str(preference.preferred_size)
    anim_size = str(animal.size)
    pref_energy = str(preference.preferred_energy)
    anim_energy = str(animal.energy_level)
    has_yard = bool(preference.has_yard)

    if pref_size == anim_size:
        score += 40

    if pref_energy == anim_energy:
        score += 40

    if has_yard:
        score += 20
    elif anim_size == "small" and anim_energy == "low":
        score += 20

    return score


def build_match_stack(db: Session, user_id: str) -> List[Dict[str, Any]]:
    preference = get_user_preferences(db, user_id)
    if not preference:
        return []

    candidates = fetch_candidate_animals(db)
    match_results = []

    for animal in candidates:
        score = calculate_score(preference, animal)
        if score >= 60:
            match_results.append(
                {
                    "id": int(str(animal.id)),
                    "foundation_id": str(animal.foundation_id),
                    "name": str(animal.name),
                    "animal_type": str(animal.animal_type),
                    "size": str(animal.size),
                    "energy_level": str(animal.energy_level),
                    "status": str(animal.status),
                    "match_score": score,
                }
            )

    match_results.sort(key=lambda x: x["match_score"], reverse=True)
    return match_results
