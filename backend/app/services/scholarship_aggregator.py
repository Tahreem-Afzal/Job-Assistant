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

    fields_lower = [f.lower() for f in scholarship.fields_of_study]
    covers_all_subjects = any("all subjects" in f for f in fields_lower)

    if params.query:
        # Split into meaningful words (3+ chars) and match if ANY word hits,
        # rather than requiring the whole phrase verbatim - "masters in
        # artificial intelligence" should still surface general scholarships
        # that fund any field, not just ones that literally say "AI".
        words = [w for w in params.query.lower().split() if len(w) >= 3]
        stopwords = {"the", "and", "for", "with", "masters", "master's", "bachelors",
                     "bachelor's", "phd", "degree", "study", "studies", "program", "programme"}
        meaningful_words = [w for w in words if w not in stopwords]

        query_hit = any(w in text for w in (meaningful_words or words))
        if not query_hit and not covers_all_subjects:
            return False

    if params.country and params.country.lower() not in (scholarship.country or "").lower():
        return False
    if params.degree_level and params.degree_level.lower() not in [
        d.lower() for d in scholarship.degree_levels
    ]:
        return False
    if params.field_of_study:
        field_lower = params.field_of_study.lower()
        if not covers_all_subjects and not any(field_lower in f for f in fields_lower):
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