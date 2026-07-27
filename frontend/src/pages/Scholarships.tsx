import { useEffect, useState, FormEvent } from "react";
import { ScholarshipResult, searchScholarships, saveScholarship } from "../api/client";

export default function Scholarships() {
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("");
  const [degreeLevel, setDegreeLevel] = useState("");
  const [scholarships, setScholarships] = useState<ScholarshipResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  async function runSearch() {
    setLoading(true);
    try {
      const res = await searchScholarships({
        q: query || undefined,
        country: country || undefined,
        degree_level: degreeLevel || undefined,
      });
      setScholarships(res.data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    runSearch();
  }

  async function handleSave(s: ScholarshipResult) {
    try {
      await saveScholarship({
        source: s.source,
        external_id: s.external_id,
        name: s.name,
        provider: s.provider,
        country: s.country,
        url: s.url,
        description: s.description,
        deadline: s.deadline,
      });
      setSavedIds((prev) => new Set(prev).add(`${s.source}-${s.external_id}`));
    } catch {
      // already saved - ignore
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Scholarships</h1>
        <p>
          A curated list of real, active fully-funded programs (DAAD, Chevening, Fulbright, Erasmus
          Mundus, and more) - not job-board keyword matching, so results are actually scholarships.
        </p>
      </div>

      <form className="search-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search by field, keyword, or program name"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <input
          type="text"
          placeholder="Country (optional)"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          style={{ maxWidth: 160 }}
        />
        <select value={degreeLevel} onChange={(e) => setDegreeLevel(e.target.value)}>
          <option value="">Any degree level</option>
          <option value="bachelors">Bachelor's</option>
          <option value="masters">Master's</option>
          <option value="phd">PhD</option>
          <option value="postdoc">Postdoc</option>
        </select>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {!loading && scholarships.length === 0 && (
        <div className="empty-state">No scholarships match those filters - try broadening your search.</div>
      )}

      <div className="job-list">
        {scholarships.map((s) => {
          const key = `${s.source}-${s.external_id}`;
          return (
            <div className="job-card" key={key}>
              <div className="job-main">
                <span className="job-source">{s.source === "curated" ? "Verified program" : s.source}</span>
                <h3>{s.name}</h3>
                <div className="job-meta">
                  {s.provider}
                  {s.country ? ` · ${s.country}` : ""}
                  {s.funding_type ? ` · ${s.funding_type.replace("_", " ")}` : ""}
                </div>
                {s.degree_levels?.length > 0 && (
                  <div className="job-meta">Degree level: {s.degree_levels.join(", ")}</div>
                )}
                {s.deadline && <div className="job-meta">Deadline: {s.deadline}</div>}
                {s.description && <div className="job-desc">{s.description}</div>}
                <div className="job-actions">
                  {s.url && (
                    <a className="btn btn-ghost btn-sm" href={s.url} target="_blank" rel="noreferrer">
                      Official page
                    </a>
                  )}
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => handleSave(s)}
                    disabled={savedIds.has(key)}
                  >
                    {savedIds.has(key) ? "Saved" : "Save"}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}