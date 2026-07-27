"""
ScholarshipAPI.com client.
Docs: https://scholarshipapi.com/
Free tier covers core fields (name, university, amount, currency, status,
dates, eligibility summary). As of writing, live coverage is Australia/NZ
universities (5,000+ scholarships) - Canada/US/EU coverage is in development
on their end, not something we control. Skips gracefully with no key set.
"""
import httpx

from app.config import settings
from app.schemas import ScholarshipResult, ScholarshipSearchParams

BASE_URL = "https://api.scholarshipapi.com/v1/scholarships"


async def search_scholarships(params: ScholarshipSearchParams) -> list[ScholarshipResult]:
    if not settings.scholarship_api_key:
        return []

    headers = {"Authorization": f"Bearer {settings.scholarship_api_key}"}
    query_params = {}
    if params.query:
        query_params["q"] = params.query
    if params.country:
        query_params["country"] = params.country

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(BASE_URL, headers=headers, params=query_params)
        except httpx.HTTPError:
            return []
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = []
    for item in data.get("data", []):
        results.append(
            ScholarshipResult(
                source="scholarshipapi",
                external_id=str(item.get("id")),
                name=item.get("name", ""),
                provider=item.get("university"),
                country=item.get("country"),
                degree_levels=item.get("academicLevels", []) or [],
                fields_of_study=item.get("eligibleDegrees", []) or [],
                funding_type=item.get("fundingType"),
                deadline=item.get("applicationDeadline") or item.get("dates"),
                url=item.get("url"),
                description=item.get("eligibilitySummary") or item.get("summary"),
            )
        )
    return results