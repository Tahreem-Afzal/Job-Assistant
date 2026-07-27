from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.services import ai_matcher

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/cover-letter", response_model=schemas.CoverLetterResponse)
def cover_letter(
    payload: schemas.CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    letter = ai_matcher.generate_cover_letter(
        profile=profile,
        job_title=payload.job_title,
        company=payload.company,
        job_description=payload.job_description,
        tone=payload.tone or "professional",
    )
    return schemas.CoverLetterResponse(cover_letter=letter)
