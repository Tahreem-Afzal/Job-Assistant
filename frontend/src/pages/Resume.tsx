import { useState, FormEvent } from "react";
import { generateCoverLetter } from "../api/client";

export default function Resume() {
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");
  const [tone, setTone] = useState("professional");
  const [letter, setLetter] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await generateCoverLetter({
        job_title: jobTitle,
        company,
        job_description: description,
        tone,
      });
      setLetter(res.data.cover_letter);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Cover letter generator</h1>
        <p>Uses your profile plus this job's details to draft a starting point.</p>
      </div>

      <form onSubmit={handleGenerate}>
        <div className="field">
          <label>Job title</label>
          <input type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} required />
        </div>
        <div className="field">
          <label>Company</label>
          <input type="text" value={company} onChange={(e) => setCompany(e.target.value)} required />
        </div>
        <div className="field">
          <label>Job description</label>
          <textarea rows={6} value={description} onChange={(e) => setDescription(e.target.value)} required />
        </div>
        <div className="field">
          <label>Tone</label>
          <select value={tone} onChange={(e) => setTone(e.target.value)}>
            <option value="professional">Professional</option>
            <option value="enthusiastic">Enthusiastic</option>
            <option value="concise">Concise</option>
          </select>
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate cover letter"}
        </button>
      </form>

      {letter && <div className="letter-output">{letter}</div>}
    </div>
  );
}
