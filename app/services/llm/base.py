from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    def validate_rescue_content(
        self, image_bytes: bytes, mime_type: str, text_content: str
    ) -> Dict[str, Any]:
        pass
