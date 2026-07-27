"""
Combines results from all configured job sources. Designed so that adding a
new source (LinkedIn later, other boards now) is just one more entry in
SOURCES plus a client module with a search_jobs(params) -> list[JobResult] fn.
"""
import asyncio
import logging

from app.schemas import JobResult, JobSearchParams
from app.services import adzuna_client, jooble_client, arbeitnow_client, findwork_client

logger = logging.getLogger(__name__)

# Sources that ignore/don't need a country param (they search globally or
# rely on the free-text location field instead).
GLOBAL_SOURCES = {
    "jooble": jooble_client.search_jobs,
    "arbeitnow": arbeitnow_client.search_jobs,
    "findwork": findwork_client.search_jobs,
}

# Countries queried when the user selects "All countries" for Adzuna, which
# requires a country code per request (no single "global" endpoint).
ADZUNA_ALL_COUNTRIES = ["gb", "us", "de", "ca", "au", "pk"]


async def _safe_call(name: str, fn, params: JobSearchParams) -> list[JobResult]:
    try:
        return await fn(params)
    except Exception as exc:  # noqa: BLE001 - one bad source shouldn't break search
        logger.warning("Job source '%s' failed: %s", name, exc)
        return []


async def _adzuna_all_countries(params: JobSearchParams) -> list[JobResult]:
    tasks = []
    for country in ADZUNA_ALL_COUNTRIES:
        country_params = params.model_copy(update={"country": country})
        tasks.append(_safe_call(f"adzuna-{country}", adzuna_client.search_jobs, country_params))
    results_per_country = await asyncio.gather(*tasks)
    merged = []
    for country_results in results_per_country:
        merged.extend(country_results)
    return merged


async def search_all(params: JobSearchParams) -> list[JobResult]:
    tasks = [_safe_call(name, fn, params) for name, fn in GLOBAL_SOURCES.items()]

    if (params.country or "").lower() == "all":
        tasks.append(_adzuna_all_countries(params))
    else:
        tasks.append(_safe_call("adzuna", adzuna_client.search_jobs, params))

    results_per_source = await asyncio.gather(*tasks)

    merged: list[JobResult] = []
    seen_titles_companies = set()
    for source_results in results_per_source:
        for job in source_results:
            key = (job.title.lower().strip(), (job.company or "").lower().strip())
            if key in seen_titles_companies:
                continue
            seen_titles_companies.add(key)
            merged.append(job)

    return merged