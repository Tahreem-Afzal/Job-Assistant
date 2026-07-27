from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = models.Profile(user_id=user.id)
    db.add(profile)
    db.commit()

    return user


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.hashed_password or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = auth.create_access_token(subject=user.id)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.post("/google", response_model=schemas.Token)
def google_login(payload: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google Sign-In is not configured on the server")

    try:
        info = google_id_token.verify_oauth2_token(
            payload.credential, google_requests.Request(), settings.google_client_id
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_id = info["sub"]
    email = info.get("email")
    full_name = info.get("name")

    user = db.query(models.User).filter(models.User.google_id == google_id).first()
    if not user:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            user.google_id = google_id
        else:
            user = models.User(email=email, full_name=full_name, google_id=google_id)
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(models.Profile(user_id=user.id))
        db.commit()
        db.refresh(user)

    token = auth.create_access_token(subject=user.id)
    return schemas.Token(access_token=token)