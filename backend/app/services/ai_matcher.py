"""
AI matching + generation layer.

Set AI_PROVIDER=groq and AI_API_KEY in .env to enable real AI-generated
cover letters. Without it (AI_PROVIDER=stub), everything still works using
a transparent keyword-overlap heuristic for matching and a template
placeholder for cover letters - useful for testing without any API key.
"""
from typing import Optional

from app.config import settings
from app.models import Profile
from app.schemas import JobResult


def _call_llm(prompt: str) -> str:
    """Single choke point for all LLM calls."""
    if settings.ai_provider == "stub" or not settings.ai_api_key:
        return "[AI generation not yet configured - set AI_PROVIDER and AI_API_KEY in .env]"

    if settings.ai_provider == "groq":
        from groq import Groq

        client = Groq(api_key=settings.ai_api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content

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

def categorize_email(subject: str, snippet: str) -> str:
    """
    Classifies an email into one of: recruiter_response, interview_invite,
    scholarship_decision, other. Stub uses keyword heuristics; swap for an
    LLM call via _call_llm once a real provider is configured, keeping the
    same string return values so callers don't change.
    """
    text = f"{subject} {snippet}".lower()

    interview_words = ["interview", "schedule a call", "meet with", "next steps", "available for a call"]
    scholarship_words = ["scholarship", "fellowship", "funding decision", "award notification", "admission decision"]
    recruiter_words = ["your application", "position", "role", "recruiter", "hiring", "candidate", "resume", "cv"]

    if any(w in text for w in interview_words):
        return "interview_invite"
    if any(w in text for w in scholarship_words):
        return "scholarship_decision"
    if any(w in text for w in recruiter_words):
        return "recruiter_response"
    return "other"


def generate_email_reply(subject: str, body: str, tone: str = "professional") -> str:
    """
    Drafts a suggested reply for the person to review and send themselves.
    This app never sends email automatically - draft-only, always.
    """
    prompt = (
        f"Write a {tone} email reply to the following message. Keep it concise "
        f"(3-5 sentences), and leave placeholders in [brackets] for anything "
        f"you can't know (like specific dates or names).\n\n"
        f"Subject: {subject}\n\nMessage:\n{body}\n"
    )
    result = _call_llm(prompt)

    if result.startswith("[AI generation not yet configured"):
        return (
            f"Hi,\n\nThank you for your email regarding \"{subject}\". "
            f"[Draft reply will appear here once an AI provider (e.g. Groq) is configured "
            f"in the backend .env - see AI_PROVIDER/AI_API_KEY]\n\nBest regards,\n[Your name]"
        )
    return result