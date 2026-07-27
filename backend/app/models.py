import uuid
import datetime as dt

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # null for Google-only accounts
    google_id = Column(String, unique=True, nullable=True, index=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    headline = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    languages = Column(JSON, default=list)

    preferred_titles = Column(JSON, default=list)
    preferred_countries = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    remote_preference = Column(String, default="any")
    min_salary = Column(Float, nullable=True)
    visa_sponsorship_required = Column(Boolean, default=False)
    desired_employment_types = Column(JSON, default=list)

    resume_text = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    source = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    raw_json = Column(JSON, nullable=True)

    status = Column(String, default="saved")
    match_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="saved_jobs")


class SavedScholarship(Base):
    __tablename__ = "saved_scholarships"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    source = Column(String, nullable=False)  # "curated" | "scholarshipapi"
    external_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    country = Column(String, nullable=True)
    url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    deadline = Column(String, nullable=True)

    status = Column(String, default="saved")  # saved | applied | submitted | awarded | rejected
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class GmailConnection(Base):
    __tablename__ = "gmail_connections"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    email_address = Column(String, nullable=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    connected_at = Column(DateTime, default=dt.datetime.utcnow)