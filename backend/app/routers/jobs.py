from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.schemas import JobSearchParams
from app.services import job_aggregator, ai_matcher

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/search", response_model=list[schemas.JobResult])
async def search_jobs(
    q: str = Query("", description="Search keywords, e.g. 'machine learning engineer'"),
    location: str | None = None,
    country: str = "pk",
    salary_min: float | None = None,
    page: int = 1,
    results_per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(auth.get_current_user),
):
    params = JobSearchParams(
        query=q,
        location=location,
        country=country,
        salary_min=salary_min,
        page=page,
        results_per_page=results_per_page,
    )
    jobs = await job_aggregator.search_all(params)

    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    for job in jobs:
        score, reason = ai_matcher.score_job_match(profile, job)
        job.match_score = score
        job.match_reason = reason

    jobs.sort(key=lambda j: j.match_score or 0, reverse=True)
    return jobs
