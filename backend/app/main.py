from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, profile, jobs, saved, ai, scholarships, saved_scholarships

# Creates tables if they don't exist. For real migrations, use Alembic instead
# (a starter alembic setup can be added once the schema stabilizes).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job & Scholarship Assistant API",
    description="AI-powered job search, matching, and application assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(saved.router)
app.include_router(ai.router)
app.include_router(scholarships.router)
app.include_router(saved_scholarships.router)


@app.get("/health")
def health():
    return {"status": "ok"}