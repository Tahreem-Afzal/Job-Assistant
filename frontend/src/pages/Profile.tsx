import { useEffect, useState, useRef } from "react";
import { Profile as ProfileType, getProfile, updateProfile, uploadResume } from "../api/client";

function ChipInput({
  label,
  values,
  onChange,
  placeholder,
}: {
  label: string;
  values: string[];
  onChange: (v: string[]) => void;
  placeholder: string;
}) {
  const [input, setInput] = useState("");

  function add() {
    const v = input.trim();
    if (v && !values.includes(v)) onChange([...values, v]);
    setInput("");
  }

  return (
    <div className="field">
      <label>{label}</label>
      <div className="chips">
        {values.map((v) => (
          <span className="chip" key={v}>
            {v}
            <button onClick={() => onChange(values.filter((x) => x !== v))}>×</button>
          </span>
        ))}
      </div>
      <input
        type="text"
        placeholder={placeholder}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            add();
          }
        }}
        onBlur={add}
      />
    </div>
  );
}

export default function Profile() {
  const [profile, setProfile] = useState<ProfileType | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getProfile().then((res) => setProfile(res.data));
  }, []);

  if (!profile) return <div className="empty-state">Loading profile...</div>;

  function update<K extends keyof ProfileType>(key: K, value: ProfileType[K]) {
    setProfile((prev) => (prev ? { ...prev, [key]: value } : prev));
    setSaved(false);
  }

  async function handleSave() {
    if (!profile) return;
    setSaving(true);
    await updateProfile(profile);
    setSaving(false);
    setSaved(true);
  }

  async function handleFileUpload(file: File) {
    setUploadError("");
    setUploading(true);
    try {
      const res = await uploadResume(file);
      setProfile(res.data);
      setSaved(false);
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail || "Upload failed - try a different file.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Your profile</h1>
        <p>This drives job matching, scoring, and generated cover letters.</p>
      </div>

      <div className="section-title">Basics</div>
      <div className="field">
        <label>Headline</label>
        <input
          type="text"
          value={profile.headline || ""}
          onChange={(e) => update("headline", e.target.value)}
          placeholder="e.g. Final-year AI student specializing in NLP and computer vision"
        />
      </div>

      <div className="section-title">Skills & preferences</div>
      <ChipInput
        label="Skills"
        values={profile.skills}
        onChange={(v) => update("skills", v)}
        placeholder="Type a skill and press Enter"
      />
      <ChipInput
        label="Preferred job titles"
        values={profile.preferred_titles}
        onChange={(v) => update("preferred_titles", v)}
        placeholder="e.g. Machine Learning Engineer"
      />
      <ChipInput
        label="Preferred countries"
        values={profile.preferred_countries}
        onChange={(v) => update("preferred_countries", v)}
        placeholder="e.g. Germany, Pakistan, Remote"
      />

      <div className="field">
        <label>Remote preference</label>
        <select
          value={profile.remote_preference}
          onChange={(e) => update("remote_preference", e.target.value)}
        >
          <option value="any">No preference</option>
          <option value="remote">Remote</option>
          <option value="hybrid">Hybrid</option>
          <option value="onsite">On-site</option>
        </select>
      </div>

      <div className="field">
        <label>
          <input
            type="checkbox"
            checked={profile.visa_sponsorship_required}
            onChange={(e) => update("visa_sponsorship_required", e.target.checked)}
            style={{ marginRight: 8 }}
          />
          I require visa sponsorship
        </label>
      </div>

      <div className="section-title">Resume (used for AI matching)</div>
      <div className="field">
        <label>Upload a file (PDF, DOCX, or TXT)</label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFileUpload(file);
          }}
        />
        {uploading && <div style={{ fontSize: 13, color: "var(--muted)" }}>Extracting text...</div>}
        {uploadError && <div className="error-text">{uploadError}</div>}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "8px 0 16px", color: "var(--muted)", fontSize: 13 }}>
        <div style={{ flex: 1, height: 1, background: "var(--slate)" }} />
        or paste it directly
        <div style={{ flex: 1, height: 1, background: "var(--slate)" }} />
      </div>

      <div className="field">
        <textarea
          rows={8}
          value={profile.resume_text || ""}
          onChange={(e) => update("resume_text", e.target.value)}
          placeholder="Paste your resume text here so matching and cover letters can reference your background."
        />
      </div>

      <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
        {saving ? "Saving..." : saved ? "Saved ✓" : "Save profile"}
      </button>
    </div>
  );
}