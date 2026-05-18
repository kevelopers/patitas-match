from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, jsonify, request


@dataclass(frozen=True)
class PetProfile:
    energy_level: int
    apartment_friendly: bool
    children_friendly: bool


class SimpleIAMatcher:
    def predict_adoption_score(self, profile: PetProfile) -> float:
        score = 0.35
        score += min(max(profile.energy_level, 1), 5) * 0.1
        score += 0.15 if profile.apartment_friendly else 0.0
        score += 0.15 if profile.children_friendly else 0.0
        return min(round(score, 2), 1.0)


def create_app() -> Flask:
    app = Flask(__name__)
    matcher = SimpleIAMatcher()

    @app.get("/")
    def home():
        return {
            "project": "patitas-match",
            "message": "Flask IA service is running",
            "endpoints": ["/predict"],
        }

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}
        try:
            profile = PetProfile(
                energy_level=int(payload["energy_level"]),
                apartment_friendly=bool(payload["apartment_friendly"]),
                children_friendly=bool(payload["children_friendly"]),
            )
        except (KeyError, TypeError, ValueError):
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

        score = matcher.predict_adoption_score(profile)
        return jsonify({"adoption_score": score})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
