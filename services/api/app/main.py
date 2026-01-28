from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import (
    create_access_token,
    get_current_user,
    get_db,
    hash_password,
    require_admin,
    verify_password,
)
from app.db import SessionLocal
from app.classifier_client import classify
from app.config import settings
from app.storage import save_photo

app = FastAPI(title="Photo Classification Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def ensure_admin_user():
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == settings.admin_email).first()
        if not existing:
            admin = models.User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.TokenResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id), user.is_admin)
    return schemas.TokenResponse(access_token=token)


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id), user.is_admin)
    return schemas.TokenResponse(access_token=token)


@app.post("/submissions", response_model=schemas.SubmissionResponse)
def create_submission(
    name: str = Form(...),
    age: int = Form(...),
    place_of_living: str = Form(...),
    gender: str = Form(...),
    country_of_origin: str = Form(...),
    description: str | None = Form(None),
    photo: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission_payload = schemas.SubmissionBase(
        name=name,
        age=age,
        place_of_living=place_of_living,
        gender=gender,
        country_of_origin=country_of_origin,
        description=description,
    )

    photo_path = save_photo(photo)
    classification = classify(submission_payload)

    record = models.Submission(
        user_id=user.id,
        name=submission_payload.name,
        age=submission_payload.age,
        place_of_living=submission_payload.place_of_living,
        gender=submission_payload.gender,
        country_of_origin=submission_payload.country_of_origin,
        description=submission_payload.description,
        photo_path=photo_path,
        classification_result=classification,
    )
    db.add(record)
    db.add(models.AuditLog(user_id=user.id, action="created_submission"))
    db.commit()
    db.refresh(record)
    return record


@app.get("/submissions/{submission_id}", response_model=schemas.SubmissionResponse)
def get_submission(
    submission_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Submission not found")
    if record.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    return record


@app.get("/admin/submissions", response_model=list[schemas.SubmissionResponse])
def list_submissions(
    age_min: int | None = None,
    age_max: int | None = None,
    gender: str | None = None,
    place_of_living: str | None = None,
    country_of_origin: str | None = None,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Submission)
    if age_min is not None:
        query = query.filter(models.Submission.age >= age_min)
    if age_max is not None:
        query = query.filter(models.Submission.age <= age_max)
    if gender:
        query = query.filter(models.Submission.gender.ilike(f"%{gender}%"))
    if place_of_living:
        query = query.filter(models.Submission.place_of_living.ilike(f"%{place_of_living}%"))
    if country_of_origin:
        query = query.filter(models.Submission.country_of_origin.ilike(f"%{country_of_origin}%"))
    return query.order_by(models.Submission.created_at.desc()).all()


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(
    request: Request,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    submissions = db.query(models.Submission).order_by(models.Submission.created_at.desc()).limit(50).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "submissions": submissions, "admin_email": admin.email},
    )
