"""
AI matching + generation layer.

Currently STUBBED with a transparent keyword-overlap heuristic so the rest of
the app is fully testable without an LLM key. Swap `settings.ai_provider` to
"groq" or "openai" and fill in the real calls in `_call_llm` when ready -
every function signature below stays the same, so nothing else in the app
needs to change.
"""
from typing import Optional

from app.config import settings
from app.models import Profile
from app.schemas import JobResult


def _call_llm(prompt: str) -> str:
    """Single choke point for all LLM calls. Replace body when wiring a real provider."""
    if settings.ai_provider == "stub" or not settings.ai_api_key:
        return "[AI generation not yet configured - set AI_PROVIDER and AI_API_KEY in .env]"

    if settings.ai_provider == "groq":
        # Example (uncomment + add `groq` to requirements.txt):
        # from groq import Groq
        # client = Groq(api_key=settings.ai_api_key)
        # resp = client.chat.completions.create(
        #     model="llama-3.3-70b-versatile",
        #     messages=[{"role": "user", "content": prompt}],
        # )
        # return resp.choices[0].message.content
        raise NotImplementedError("Wire up Groq client here")

    if settings.ai_provider == "openai":
        raise NotImplementedError("Wire up OpenAI client here")

    return "[Unknown AI provider configured]"


def score_job_match(profile: Optional[Profile], job: JobResult) -> tuple[float, str]:
    """
    Returns (score 0-100, one-line reason).
    Stub: simple weighted overlap between profile skills/titles and job text.
    Replace with an LLM-graded match once AI_PROVIDER is configured -
    keep the same return shape so callers don't change.
    """
    if profile is None:
        return 0.0, "No profile set up yet - add your skills for personalized matching."

    job_text = f"{job.title} {job.description or ''}".lower()

    skills = [s.lower() for s in (profile.skills or [])]
    titles = [t.lower() for t in (profile.preferred_titles or [])]

    skill_hits = [s for s in skills if s in job_text]
    title_hits = [t for t in titles if t in job_text]

    skill_score = (len(skill_hits) / len(skills) * 70) if skills else 0
    title_score = 30 if title_hits else 0
    score = round(min(skill_score + title_score, 100), 1)

    if skill_hits:
        reason = f"Matches {len(skill_hits)} of your skills: {', '.join(skill_hits[:4])}"
    elif title_hits:
        reason = "Matches one of your preferred job titles"
    else:
        reason = "Limited overlap with your current profile - review details before applying"

    return score, reason


def generate_cover_letter(
    profile: Optional[Profile], job_title: str, company: str, job_description: str, tone: str = "professional"
) -> str:
    skills = ", ".join((profile.skills if profile else []) or ["your relevant skills"])
    headline = (profile.headline if profile else None) or "a motivated candidate"

    prompt = (
        f"Write a {tone} cover letter for a {job_title} position at {company}.\n"
        f"Candidate background: {headline}. Key skills: {skills}.\n"
        f"Job description: {job_description}\n"
    )
    result = _call_llm(prompt)

    if result.startswith("[AI generation not yet configured"):
        # Friendly placeholder so the feature is demoable before an LLM key exists
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my interest in the {job_title} position at {company}. "
            f"As {headline}, with experience in {skills}, I believe I would be a strong fit for this role.\n\n"
            f"[Full AI-generated draft will appear here once an AI provider is configured in .env]\n\n"
            f"Sincerely,\n{profile.headline if profile else 'Candidate'}"
        )
    return result
