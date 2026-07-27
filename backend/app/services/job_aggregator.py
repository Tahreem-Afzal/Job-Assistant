"""
Combines results from all configured job sources. Designed so that adding a
new source (LinkedIn later, other boards now) is just one more entry in
SOURCES plus a client module with a search_jobs(params) -> list[JobResult] fn.
"""
import asyncio
import logging

from app.schemas import JobResult, JobSearchParams
from app.services import adzuna_client, jooble_client

logger = logging.getLogger(__name__)

SOURCES = {
    "adzuna": adzuna_client.search_jobs,
    "jooble": jooble_client.search_jobs,
}


async def _safe_call(name: str, fn, params: JobSearchParams) -> list[JobResult]:
    try:
        return await fn(params)
    except Exception as exc:  # noqa: BLE001 - one bad source shouldn't break search
        logger.warning("Job source '%s' failed: %s", name, exc)
        return []


async def search_all(params: JobSearchParams) -> list[JobResult]:
    tasks = [_safe_call(name, fn, params) for name, fn in SOURCES.items()]
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
