"""
Merges the curated scholarship list with live ScholarshipAPI.com results
(where available) and filters/scores against search params and profile.
"""
import logging

from app.schemas import ScholarshipResult, ScholarshipSearchParams
from app.services.scholarship_curated import CURATED_SCHOLARSHIPS
from app.services import scholarship_api_client

logger = logging.getLogger(__name__)


def _matches(scholarship: ScholarshipResult, params: ScholarshipSearchParams) -> bool:
    text = " ".join(
        [
            scholarship.name,
            scholarship.provider or "",
            scholarship.description or "",
            " ".join(scholarship.fields_of_study),
        ]
    ).lower()

    if params.query and params.query.lower() not in text:
        return False
    if params.country and params.country.lower() not in (scholarship.country or "").lower():
        return False
    if params.degree_level and params.degree_level.lower() not in [
        d.lower() for d in scholarship.degree_levels
    ]:
        return False
    if params.field_of_study:
        field_lower = params.field_of_study.lower()
        if not any(field_lower in f.lower() for f in scholarship.fields_of_study):
            return False
    return True


async def search_all(params: ScholarshipSearchParams) -> list[ScholarshipResult]:
    results: list[ScholarshipResult] = list(CURATED_SCHOLARSHIPS)

    try:
        api_results = await scholarship_api_client.search_scholarships(params)
        results.extend(api_results)
    except Exception as exc:  # noqa: BLE001 - one bad source shouldn't break search
        logger.warning("ScholarshipAPI source failed: %s", exc)

    return [s for s in results if _matches(s, params)]