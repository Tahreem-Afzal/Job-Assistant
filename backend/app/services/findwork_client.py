"""
Findwork.dev API client - free API key required (sign up at findwork.dev).
Docs: https://findwork.dev/developers/
Aggregates dev/design jobs from Hacker News, RemoteOK, WeWorkRemotely, Dribbble.
"""
import httpx

from app.config import settings
from app.schemas import JobResult, JobSearchParams

BASE_URL = "https://findwork.dev/api/jobs/"


async def search_jobs(params: JobSearchParams) -> list[JobResult]:
    if not settings.findwork_api_key:
        return []

    headers = {"Authorization": f"Token {settings.findwork_api_key}"}
    query_params = {}
    if params.query:
        query_params["search"] = params.query
    if params.location:
        query_params["location"] = params.location

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(BASE_URL, headers=headers, params=query_params)
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = []
    for item in data.get("results", [])[: params.results_per_page]:
        results.append(
            JobResult(
                source="findwork",
                external_id=str(item.get("id")),
                title=item.get("role", ""),
                company=item.get("company_name"),
                location=item.get("location"),
                url=item.get("url"),
                description=item.get("text"),
                salary_min=None,
                salary_max=None,
                posted_at=item.get("date_posted"),
                employment_type=item.get("employment_type"),
                raw=item,
            )
        )
    return results