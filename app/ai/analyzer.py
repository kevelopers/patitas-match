from transformers import pipeline
from PIL import Image
import io


class ImageAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            "image-classification", model="google/vit-base-patch16-224"
        )

    def analyze_image(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes))
        results = self.classifier(image)
        tags = [result["label"] for result in results[:3]]
        return ", ".join(tags)


analyzer_instance = ImageAnalyzer()


def process_rescue_image(image_bytes: bytes) -> str:
    return analyzer_instance.analyze_image(image_bytes)
