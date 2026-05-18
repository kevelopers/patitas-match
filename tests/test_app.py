import unittest

from app import create_app


class TestPredictEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    def test_home_reports_service(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["project"], "patitas-match")
        self.assertIn("/predict", body["endpoints"])

    def test_predict_returns_score(self):
        response = self.app.post(
            "/predict",
            json={
                "energy_level": 4,
                "apartment_friendly": True,
                "children_friendly": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn("adoption_score", body)
        self.assertGreaterEqual(body["adoption_score"], 0)
        self.assertLessEqual(body["adoption_score"], 1)

    def test_predict_validates_payload(self):
        invalid_payloads = [
            {"energy_level": "high", "apartment_friendly": True, "children_friendly": True},
            {"energy_level": 3, "apartment_friendly": "true", "children_friendly": True},
            {"energy_level": 8, "apartment_friendly": True, "children_friendly": True},
            {"energy_level": 3, "apartment_friendly": True},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.app.post("/predict", json=payload)
                self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
