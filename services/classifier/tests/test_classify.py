from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)


def test_classify_minor():
    response = client.post(
        "/classify",
        json={
            "name": "Jane",
            "age": 12,
            "place_of_living": "Berlin",
            "gender": "female",
            "country_of_origin": "DE",
            "description": None,
        },
    )
    assert response.status_code == 200
    assert response.json()["label"] == "minor"


def test_classify_technical():
    response = client.post(
        "/classify",
        json={
            "name": "Alex",
            "age": 30,
            "place_of_living": "Paris",
            "gender": "male",
            "country_of_origin": "FR",
            "description": "software engineer",
        },
    )
    assert response.status_code == 200
    assert response.json()["label"] == "technical"
