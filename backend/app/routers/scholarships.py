from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.schemas import ScholarshipSearchParams
from app.services import scholarship_aggregator

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


@router.get("/search", response_model=list[schemas.ScholarshipResult])
async def search_scholarships(
    q: str = "",
    country: str | None = None,
    degree_level: str | None = None,
    field_of_study: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    params = ScholarshipSearchParams(
        query=q,
        country=country,
        degree_level=degree_level,
        field_of_study=field_of_study,
    )
    scholarships = await scholarship_aggregator.search_all(params)

    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    for s in scholarships:
        skills = [sk.lower() for sk in (profile.skills if profile else [])]
        text = f"{s.name} {s.description or ''}".lower()
        hits = [sk for sk in skills if sk in text]
        s.match_score = min(len(hits) * 20, 100) if skills else None
        s.match_reason = (
            f"Related to your background: {', '.join(hits[:3])}" if hits else None
        )

    return scholarships