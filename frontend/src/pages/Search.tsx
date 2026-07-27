import { useState, FormEvent } from "react";
import { JobResult, searchJobs, saveJob } from "../api/client";
import JobCard from "../components/JobCard";

export default function Search() {
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [country, setCountry] = useState("pk");
  const [jobs, setJobs] = useState<JobResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState("");

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await searchJobs({ q: query, location: location || undefined, country });
      setJobs(res.data);
      setSearched(true);
    } catch (err: any) {
      setError("Search failed - check that the backend is running and API keys are configured.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(job: JobResult) {
    try {
      await saveJob({
        source: job.source,
        external_id: job.external_id,
        title: job.title,
        company: job.company,
        location: job.location,
        url: job.url,
        description: job.description,
        salary_min: job.salary_min,
        salary_max: job.salary_max,
      });
      setSavedIds((prev) => new Set(prev).add(`${job.source}-${job.external_id}`));
    } catch {
      // already saved or other error - ignore silently for now
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Find your next role</h1>
        <p>Searches multiple job boards at once and ranks results against your profile.</p>
      </div>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Job title or keywords, e.g. Machine Learning Engineer"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <input
          type="text"
          placeholder="Location (optional)"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          style={{ maxWidth: 200 }}
        />
        <select value={country} onChange={(e) => setCountry(e.target.value)}>
          <option value="pk">Pakistan</option>
          <option value="gb">UK</option>
          <option value="us">US</option>
          <option value="de">Germany</option>
          <option value="ca">Canada</option>
        </select>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <div className="error-text">{error}</div>}

      {!searched && !loading && (
        <div className="empty-state">Search above to see matching roles from Adzuna and Jooble.</div>
      )}

      {searched && !loading && jobs.length === 0 && !error && (
        <div className="empty-state">
          No results. If ADZUNA_APP_ID/APP_KEY and JOOBLE_API_KEY aren't set in the backend .env yet,
          add them to see live results.
        </div>
      )}

      <div className="job-list">
        {jobs.map((job) => (
          <JobCard
            key={`${job.source}-${job.external_id}`}
            job={job}
            onSave={handleSave}
            saved={savedIds.has(`${job.source}-${job.external_id}`)}
          />
        ))}
      </div>
    </div>
  );
}
