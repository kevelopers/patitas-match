from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, jsonify, request


@dataclass(frozen=True)
class PetProfile:
    energy_level: int
    apartment_friendly: bool
    children_friendly: bool


class SimpleAIMatcher:
    BASE_SCORE = 0.35
    MIN_ENERGY_LEVEL = 1
    MAX_ENERGY_LEVEL = 5
    ENERGY_WEIGHT = 0.1
    APARTMENT_WEIGHT = 0.15
    CHILDREN_WEIGHT = 0.15

    def predict_adoption_score(self, profile: PetProfile) -> float:
        """Return a score in [0, 1] from a lightweight rule-based AI model."""
        score = self.BASE_SCORE
        score += profile.energy_level * self.ENERGY_WEIGHT
        score += self.APARTMENT_WEIGHT if profile.apartment_friendly else 0.0
        score += self.CHILDREN_WEIGHT if profile.children_friendly else 0.0
        return min(round(score, 2), 1.0)


def create_app() -> Flask:
    app = Flask(__name__)
    matcher = SimpleAIMatcher()

    @app.get("/")
    def home():
        return {
            "project": "patitas-match",
            "message": "Flask AI service is running",
            "endpoints": ["/predict"],
        }

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}
        energy_level = payload.get("energy_level")
        apartment_friendly = payload.get("apartment_friendly")
        children_friendly = payload.get("children_friendly")

        valid_energy = (
            isinstance(energy_level, int)
            and not isinstance(energy_level, bool)
            and (
                SimpleAIMatcher.MIN_ENERGY_LEVEL
                <= energy_level
                <= SimpleAIMatcher.MAX_ENERGY_LEVEL
            )
        )
        valid_booleans = isinstance(apartment_friendly, bool) and isinstance(
            children_friendly, bool
        )

        if not (valid_energy and valid_booleans):
            return (
                jsonify(
                    {
                        "error": (
                            "Invalid payload. Required fields: energy_level, "
                            "apartment_friendly, children_friendly."
                        )
                    }
                ),
                400,
            )
        profile = PetProfile(
            energy_level=energy_level,
            apartment_friendly=apartment_friendly,
            children_friendly=children_friendly,
        )

        score = matcher.predict_adoption_score(profile)
        return jsonify({"adoption_score": score})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
