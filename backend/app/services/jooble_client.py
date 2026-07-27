"""
Jooble Job Search API client.
Docs: https://jooble.org/api/about
Free tier: request an API key at jooble.org/api/about.
"""
import httpx

from app.config import settings
from app.schemas import JobResult, JobSearchParams

BASE_URL = "https://jooble.org/api"


async def search_jobs(params: JobSearchParams) -> list[JobResult]:
    if not settings.jooble_api_key:
        return []

    url = f"{BASE_URL}/{settings.jooble_api_key}"
    payload = {
        "keywords": params.query,
        "location": params.location or "",
        "page": str(params.page),
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = []
    for item in data.get("jobs", []):
        results.append(
            JobResult(
                source="jooble",
                external_id=str(item.get("id") or item.get("link")),
                title=(item.get("title") or "").strip(),
                company=item.get("company"),
                location=item.get("location"),
                url=item.get("link"),
                description=item.get("snippet"),
                salary_min=None,
                salary_max=None,
                posted_at=item.get("updated"),
                employment_type=item.get("type"),
                raw=item,
            )
        )
    return results
