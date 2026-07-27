from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/saved-scholarships", tags=["saved-scholarships"])


@router.get("", response_model=list[schemas.SavedScholarshipOut])
def list_saved(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.SavedScholarship).filter(models.SavedScholarship.user_id == current_user.id)
    if status:
        query = query.filter(models.SavedScholarship.status == status)
    return query.order_by(models.SavedScholarship.created_at.desc()).all()


@router.post("", response_model=schemas.SavedScholarshipOut, status_code=201)
def save_scholarship(
    payload: schemas.SavedScholarshipCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = (
        db.query(models.SavedScholarship)
        .filter(
            models.SavedScholarship.user_id == current_user.id,
            models.SavedScholarship.source == payload.source,
            models.SavedScholarship.external_id == payload.external_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Scholarship already saved")

    scholarship = models.SavedScholarship(user_id=current_user.id, **payload.model_dump())
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    return scholarship


@router.patch("/{scholarship_id}", response_model=schemas.SavedScholarshipOut)
def update_saved_scholarship(
    scholarship_id: str,
    payload: schemas.SavedScholarshipUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    scholarship = (
        db.query(models.SavedScholarship)
        .filter(models.SavedScholarship.id == scholarship_id, models.SavedScholarship.user_id == current_user.id)
        .first()
    )
    if not scholarship:
        raise HTTPException(status_code=404, detail="Saved scholarship not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(scholarship, field, value)

    db.commit()
    db.refresh(scholarship)
    return scholarship


@router.delete("/{scholarship_id}", status_code=204)
def delete_saved_scholarship(
    scholarship_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    scholarship = (
        db.query(models.SavedScholarship)
        .filter(models.SavedScholarship.id == scholarship_id, models.SavedScholarship.user_id == current_user.id)
        .first()
    )
    if not scholarship:
        raise HTTPException(status_code=404, detail="Saved scholarship not found")
    db.delete(scholarship)
    db.commit()
    return None