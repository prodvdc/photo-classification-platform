from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Photo Classification Service")


class ClassificationRequest(BaseModel):
    name: str
    age: int
    place_of_living: str
    gender: str
    country_of_origin: str
    description: str | None = None


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/classify")
def classify(payload: ClassificationRequest):
    label = "standard"
    if payload.age < 18:
        label = "minor"
    elif "engineer" in (payload.description or "").lower():
        label = "technical"
    elif payload.gender.lower().startswith("f"):
        label = "category-f"

    return {"label": label}
