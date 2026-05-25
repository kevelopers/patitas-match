import os
import base64
import json
import logging
import time
import requests
from typing import Dict, Any
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "empty_api_key")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        self._verify_credentials()

    def _verify_credentials(self) -> None:
        if self.api_key == "empty_api_key":
            logger.error(
                "CRITICAL: GEMINI_API_KEY environment variable is missing or set to default empty value."
            )
        else:
            logger.info(
                f"GeminiProvider successfully initialized with active key prefix: {self.api_key[:6]}"
            )

    def validate_rescue_content(
        self, image_bytes: bytes, mime_type: str, text_content: str
    ) -> Dict[str, Any]:
        if self.api_key == "empty_api_key":
            return self._get_fallback_response(False)

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        prompt = (
            "Analyze the provided image and text description.\n"
            "Determine if the visual subject is a real, live animal (e.g., dog, cat, bird, rabbit).\n"
            "Strictly reject inanimate objects, furniture, humans, or fictional creatures.\n"
            "Context text from reporter: " + text_content + "\n\n"
            "If valid, analyze and extract the following parameters:\n"
            "1. tags: Up to 3 tags in Spanish, separated by commas. Single-word entirely lowercase. Compound words in camelCase.\n"
            "2. urgency: Classify priority strictly as 'low', 'high', or 'critical' based on health state, immediate danger or traffic risk.\n"
            "3. breed_mix: Best estimate of breed mix or purebred status in Spanish (e.g., 'Mestizo de Poodle', 'Pastor Alemán Mix', 'Mestizo').\n"
            "4. detected_mood: Current emotional state visible (e.g., 'Asustado', 'Alerta', 'Tranquilo', 'Agresivo').\n"
            "5. physical_condition: Observed physical health status (e.g., 'Estable', 'Desnutrición leve', 'Herida visible', 'Cojera').\n"
            "6. first_aid_advice: Short, 2-line practical first aid recommendation in Spanish for the citizen on site.\n\n"
            "Return a valid JSON object matching exactly this schema:\n"
            "{\n"
            '  "valid": true,\n'
            '  "tags": "perro, callejero, asustado",\n'
            '  "urgency": "high",\n'
            '  "breed_mix": "Mestizo de Schnauzer",\n'
            '  "detected_mood": "Asustado",\n'
            '  "physical_condition": "Estable",\n'
            '  "first_aid_advice": "Evita movimientos bruscos y no lo arrincones. Ofrécele agua limpia."\n'
            "}\n"
            "If the subject is NOT a live animal, return strictly:\n"
            '{"valid": false, "tags": "INVALID_CONTENT", "urgency": "low", "breed_mix": "N/A", "detected_mood": "N/A", "physical_condition": "N/A", "first_aid_advice": ""}\n'
            "Do not include markdown formatting or backticks."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"inlineData": {"mimeType": mime_type, "data": base64_image}},
                        {"text": prompt},
                    ]
                }
            ],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        headers = {"Content-Type": "application/json"}
        max_retries = 3
        initial_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, json=payload, headers=headers)
                logger.info(f"Gemini API Response Status: {response.status_code}")

                if response.status_code == 200:
                    result_json = response.json()
                    text_response = result_json["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    logger.info(f"Gemini API Raw Text Response: {text_response}")

                    cleaned_text = self._clean_json_response(text_response)
                    parsed_response = json.loads(cleaned_text)
                    return parsed_response

                if response.status_code in {429, 503} and attempt < max_retries - 1:
                    sleep_time = initial_delay * (2**attempt)
                    logger.warning(
                        f"Transient error {response.status_code} encountered. Retrying in {sleep_time} seconds..."
                    )
                    time.sleep(sleep_time)
                    continue

                logger.error(f"Gemini API Error Payload: {response.text}")
                return self._get_fallback_response(False)

            except Exception as error:
                logger.error(
                    f"Failed to process Gemini response workflow on attempt {attempt + 1}: {str(error)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(initial_delay * (2**attempt))
                    continue
                return self._get_fallback_response(False)

        return self._get_fallback_response(False)

    def _clean_json_response(self, raw_text: str) -> str:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        return cleaned

    def _get_fallback_response(self, is_valid: bool) -> Dict[str, Any]:
        return {
            "valid": is_valid,
            "tags": (
                "INVALID_CONTENT" if not is_valid else "animal, resguardado, alerta"
            ),
            "urgency": "low",
            "breed_mix": "Mestizo Desconocido",
            "detected_mood": "Alerta",
            "physical_condition": "Estable",
            "first_aid_advice": "Mantener distancia segura, no acorralar al animal y proveer agua limpia de ser posible.",
        }
