from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/saved-jobs", tags=["saved-jobs"])


@router.get("", response_model=list[schemas.SavedJobOut])
def list_saved(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.SavedJob).filter(models.SavedJob.user_id == current_user.id)
    if status:
        query = query.filter(models.SavedJob.status == status)
    return query.order_by(models.SavedJob.created_at.desc()).all()


@router.post("", response_model=schemas.SavedJobOut, status_code=201)
def save_job(
    payload: schemas.SavedJobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = (
        db.query(models.SavedJob)
        .filter(
            models.SavedJob.user_id == current_user.id,
            models.SavedJob.source == payload.source,
            models.SavedJob.external_id == payload.external_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")

    job = models.SavedJob(user_id=current_user.id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=schemas.SavedJobOut)
def update_saved_job(
    job_id: str,
    payload: schemas.SavedJobUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    job = (
        db.query(models.SavedJob)
        .filter(models.SavedJob.id == job_id, models.SavedJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Saved job not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_saved_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    job = (
        db.query(models.SavedJob)
        .filter(models.SavedJob.id == job_id, models.SavedJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(job)
    db.commit()
    return None
