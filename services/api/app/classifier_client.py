import requests

from app.config import settings
from app.schemas import SubmissionBase


def classify(payload: SubmissionBase) -> str:
    response = requests.post(
        f"{settings.classifier_url}/classify",
        json=payload.dict(),
        timeout=5,
    )
    response.raise_for_status()
    return response.json().get("label", "unknown")
