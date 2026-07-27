from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class GoogleAuthRequest(BaseModel):
    credential: str  # the ID token returned by Google Identity Services


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Profile ----------
class ProfileUpdate(BaseModel):
    headline: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[dict]] = None
    experience: Optional[List[dict]] = None
    languages: Optional[List[str]] = None
    preferred_titles: Optional[List[str]] = None
    preferred_countries: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    min_salary: Optional[float] = None
    visa_sponsorship_required: Optional[bool] = None
    desired_employment_types: Optional[List[str]] = None
    resume_text: Optional[str] = None


class ProfileOut(ProfileUpdate):
    id: str

    class Config:
        from_attributes = True


# ---------- Jobs (external, not DB-backed) ----------
class JobResult(BaseModel):
    source: str
    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    posted_at: Optional[str] = None
    employment_type: Optional[str] = None
    match_score: Optional[float] = None
    match_reason: Optional[str] = None
    raw: Optional[Any] = None


class JobSearchParams(BaseModel):
    query: str = ""
    location: Optional[str] = None
    country: Optional[str] = "pk"
    remote_only: bool = False
    salary_min: Optional[float] = None
    page: int = 1
    results_per_page: int = 20


# ---------- Saved jobs ----------
class SavedJobCreate(BaseModel):
    source: str
    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    raw_json: Optional[dict] = None


class SavedJobUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class SavedJobOut(BaseModel):
    id: str
    source: str
    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: str
    match_score: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- AI ----------
class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    tone: Optional[str] = "professional"


class CoverLetterResponse(BaseModel):
    cover_letter: str


class MatchExplainRequest(BaseModel):
    job_title: str
    job_description: str


# ---------- Scholarships (external + curated, not fully DB-backed) ----------
class ScholarshipResult(BaseModel):
    source: str  # "curated" | "scholarshipapi"
    external_id: str
    name: str
    provider: Optional[str] = None
    country: Optional[str] = None
    degree_levels: List[str] = []
    fields_of_study: List[str] = []
    funding_type: Optional[str] = None
    deadline: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    match_score: Optional[float] = None
    match_reason: Optional[str] = None


class ScholarshipSearchParams(BaseModel):
    query: str = ""
    country: Optional[str] = None
    degree_level: Optional[str] = None
    field_of_study: Optional[str] = None


class SavedScholarshipCreate(BaseModel):
    source: str
    external_id: str
    name: str
    provider: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None


class SavedScholarshipUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class SavedScholarshipOut(BaseModel):
    id: str
    source: str
    external_id: str
    name: str
    provider: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True