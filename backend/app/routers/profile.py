from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.services import resume_parser

router = APIRouter(prefix="/profile", tags=["profile"])

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("", response_model=schemas.ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=schemas.ProfileOut)
def update_profile(
    payload: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/resume-upload", response_model=schemas.ProfileOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    content = await file.read()
    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        extracted_text = resume_parser.extract_text(file.filename or "", content)
    except resume_parser.UnsupportedFileType as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Couldn't extract any text from that file - it may be a scanned/image-based PDF.",
        )

    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.resume_text = extracted_text
    db.commit()
    db.refresh(profile)
    return profile