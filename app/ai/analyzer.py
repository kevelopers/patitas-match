from transformers import pipeline
from PIL import Image
import io


class ImageAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-image-classification", model="openai/clip-vit-base-patch32"
        )

    def analyze_image(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes))
        labels = [
            "a dog",
            "a cat",
            "an animal",
            "human food",
            "a car",
            "a person",
            "an object",
        ]

        results = self.classifier(image, candidate_labels=labels)

        top_label = results[0]["label"]
        score = results[0]["score"]
        animal_labels = ["a dog", "a cat", "an animal"]

        if top_label not in animal_labels and score > 0.6:
            return "INVALID_CONTENT"

        return top_label.replace("a ", "")


analyzer_instance = ImageAnalyzer()


def process_rescue_image(image_bytes: bytes) -> str:
    return analyzer_instance.analyze_image(image_bytes)
