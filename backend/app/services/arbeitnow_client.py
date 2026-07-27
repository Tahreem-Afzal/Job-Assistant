"""
Arbeitnow API client - free, no API key required.
Docs: https://www.arbeitnow.com/api/job-board-api
Covers European tech jobs, remote roles, visa sponsorship listings.
Note: Arbeitnow has no server-side search param - we fetch recent listings
and filter by keyword/location client-side.
"""
import httpx

from app.schemas import JobResult, JobSearchParams

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


async def search_jobs(params: JobSearchParams) -> list[JobResult]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(BASE_URL)
        if resp.status_code != 200:
            return []
        data = resp.json()

    query_lower = (params.query or "").lower()
    location_lower = (params.location or "").lower()

    results = []
    for item in data.get("data", []):
        title = item.get("title", "")
        description = item.get("description", "")
        location = item.get("location", "")

        if query_lower and query_lower not in title.lower() and query_lower not in description.lower():
            continue
        if location_lower and location_lower not in location.lower():
            continue

        results.append(
            JobResult(
                source="arbeitnow",
                external_id=item.get("slug", str(item.get("url", ""))),
                title=title,
                company=item.get("company_name"),
                location=location or ("Remote" if item.get("remote") else None),
                url=item.get("url"),
                description=description,
                salary_min=None,
                salary_max=None,
                posted_at=str(item.get("created_at", "")),
                employment_type=", ".join(item.get("job_types", []) or []),
                raw=item,
            )
        )
    return results[: params.results_per_page]