"""
Adzuna Job Search API client.
Docs: https://developer.adzuna.com/
Free tier: sign up at developer.adzuna.com for app_id + app_key.
"""
import httpx

from app.config import settings
from app.schemas import JobResult, JobSearchParams

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


async def search_jobs(params: JobSearchParams) -> list[JobResult]:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return []

    country = (params.country or "pk").lower()
    url = f"{BASE_URL}/{country}/search/{params.page}"

    query_params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": params.results_per_page,
        "what": params.query,
        "content-type": "application/json",
    }
    if params.location:
        query_params["where"] = params.location
    if params.salary_min:
        query_params["salary_min"] = params.salary_min

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=query_params)
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = []
    for item in data.get("results", []):
        results.append(
            JobResult(
                source="adzuna",
                external_id=str(item.get("id")),
                title=item.get("title", "").strip(),
                company=(item.get("company") or {}).get("display_name"),
                location=(item.get("location") or {}).get("display_name"),
                url=item.get("redirect_url"),
                description=item.get("description"),
                salary_min=item.get("salary_min"),
                salary_max=item.get("salary_max"),
                posted_at=item.get("created"),
                employment_type=item.get("contract_time"),
                raw=item,
            )
        )
    return results
