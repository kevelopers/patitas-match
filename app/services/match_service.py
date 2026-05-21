from typing import Any, Dict, List, Set
from sqlalchemy.orm import Session
from app.models.user import UserPreference
from app.models.animal import Animal
from app.models.match import Match, Rejection


def _extract_preference_set(preferences: UserPreference, attribute: str) -> Set[str]:
    value = getattr(preferences, attribute, [])
    if isinstance(value, list):
        return set(value)
    return set()


def _check_yard_availability(preferences: UserPreference) -> bool:
    return getattr(preferences, "has_yard", False) is True


def _calculate_compatibility_score(
    animal: Animal,
    target_sizes: Set[str],
    target_energies: Set[str],
    target_ages: Set[str],
    has_yard: bool,
) -> int:
    score = 0
    animal_size = str(getattr(animal, "size", ""))
    animal_energy = str(getattr(animal, "energy_level", ""))
    animal_age = str(getattr(animal, "age", ""))

    if animal_size in target_sizes:
        score += 30

    if animal_energy in target_energies:
        score += 30

    if animal_age and animal_age in target_ages:
        score += 20

    if animal_energy == "high":
        if has_yard:
            score += 20
        else:
            score -= 20

    return max(0, min(100, score + 20))


def get_user_match_stack(db: Session, user_id: str) -> List[Dict[str, Any]]:
    preferences = (
        db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    )
    available_animals = db.query(Animal).filter(Animal.status == "available").all()

    existing_matches = db.query(Match).filter(Match.user_id == user_id).all()
    existing_rejections = db.query(Rejection).filter(Rejection.user_id == user_id).all()

    excluded_animal_ids = {interaction.animal_id for interaction in existing_matches}
    excluded_animal_ids.update(rejection.animal_id for rejection in existing_rejections)

    if not preferences:
        fallback_results = []
        for animal in available_animals:
            if animal.id in excluded_animal_ids:
                continue
            fallback_results.append(
                {
                    "id": getattr(animal, "id", ""),
                    "name": getattr(animal, "name", ""),
                    "size": getattr(animal, "size", ""),
                    "energy_level": getattr(animal, "energy_level", ""),
                    "match_score": 50,
                }
            )
        return fallback_results

    target_sizes = _extract_preference_set(preferences, "preferred_size")
    target_energies = _extract_preference_set(preferences, "preferred_energy")
    target_ages = _extract_preference_set(preferences, "preferred_age")
    has_yard = _check_yard_availability(preferences)

    match_results = []
    for animal in available_animals:
        if animal.id in excluded_animal_ids:
            continue
        score = _calculate_compatibility_score(
            animal, target_sizes, target_energies, target_ages, has_yard
        )
        match_results.append(
            {
                "id": getattr(animal, "id", ""),
                "name": getattr(animal, "name", ""),
                "size": getattr(animal, "size", ""),
                "energy_level": getattr(animal, "energy_level", ""),
                "match_score": score,
            }
        )

    match_results.sort(key=lambda item: item["match_score"], reverse=True)
    return match_results
