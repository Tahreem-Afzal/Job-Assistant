import { useEffect, useState } from "react";
import { SavedJob, listSavedJobs, updateSavedJob, deleteSavedJob } from "../api/client";

const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];

function StatusTrail({ job, onChange }: { job: SavedJob; onChange: (status: string) => void }) {
  return (
    <div className="status-trail">
      {STATUSES.map((s) => (
        <button
          key={s}
          className={`step ${job.status === s ? (s === "rejected" ? "rejected" : "active") : ""}`}
          onClick={() => onChange(s)}
        >
          {s}
        </button>
      ))}
    </div>
  );
}

export default function Saved() {
  const [jobs, setJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    const res = await listSavedJobs();
    setJobs(res.data);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  async function handleStatusChange(id: string, status: string) {
    await updateSavedJob(id, { status });
    setJobs((prev) => prev.map((j) => (j.id === id ? { ...j, status } : j)));
  }

  async function handleDelete(id: string) {
    await deleteSavedJob(id);
    setJobs((prev) => prev.filter((j) => j.id !== id));
  }

  return (
    <div>
      <div className="page-header">
        <h1>Saved jobs</h1>
        <p>Track where each application stands.</p>
      </div>

      {loading && <div className="empty-state">Loading...</div>}
      {!loading && jobs.length === 0 && (
        <div className="empty-state">No saved jobs yet — save roles from Search to track them here.</div>
      )}

      <div className="job-list">
        {jobs.map((job) => (
          <div className="job-card" key={job.id}>
            <div className="job-main">
              <span className="job-source">{job.source}</span>
              <h3>{job.title}</h3>
              <div className="job-meta">
                {job.company || "Unknown company"}
                {job.location ? ` · ${job.location}` : ""}
              </div>
              <StatusTrail job={job} onChange={(s) => handleStatusChange(job.id, s)} />
              <div className="job-actions">
                {job.url && (
                  <a className="btn btn-ghost btn-sm" href={job.url} target="_blank" rel="noreferrer">
                    View posting
                  </a>
                )}
                <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(job.id)}>
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
