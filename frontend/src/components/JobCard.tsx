import { JobResult } from "../api/client";

function MatchCompass({ score }: { score?: number }) {
  const value = score ?? 0;
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const color = value >= 70 ? "var(--gold)" : value >= 40 ? "var(--muted)" : "var(--slate)";

  return (
    <div className="match-compass">
      <svg width="68" height="68" viewBox="0 0 68 68">
        <circle cx="34" cy="34" r={radius} fill="none" stroke="var(--slate)" strokeWidth="5" />
        <circle
          cx="34"
          cy="34"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="score-value">{score != null ? Math.round(score) : "—"}</span>
      <span className="score-label">match</span>
    </div>
  );
}

export default function JobCard({
  job,
  onSave,
  saved,
}: {
  job: JobResult;
  onSave?: (job: JobResult) => void;
  saved?: boolean;
}) {
  return (
    <div className="job-card">
      <MatchCompass score={job.match_score} />
      <div className="job-main">
        <span className="job-source">{job.source}</span>
        <h3>{job.title}</h3>
        <div className="job-meta">
          {job.company || "Unknown company"}
          {job.location ? ` · ${job.location}` : ""}
          {job.salary_min ? ` · from ${job.salary_min.toLocaleString()}` : ""}
        </div>
        {job.match_reason && (
          <div className="job-meta" style={{ color: "var(--gold-soft)" }}>
            {job.match_reason}
          </div>
        )}
        {job.description && <div className="job-desc">{job.description}</div>}
        <div className="job-actions">
          {job.url && (
            <a className="btn btn-ghost btn-sm" href={job.url} target="_blank" rel="noreferrer">
              View posting
            </a>
          )}
          {onSave && (
            <button className="btn btn-primary btn-sm" onClick={() => onSave(job)} disabled={saved}>
              {saved ? "Saved" : "Save job"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
