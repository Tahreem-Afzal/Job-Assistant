import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Types ----------
export interface User {
  id: string;
  email: string;
  full_name?: string;
}

export interface Profile {
  id: string;
  headline?: string;
  skills: string[];
  education: Record<string, any>[];
  experience: Record<string, any>[];
  languages: string[];
  preferred_titles: string[];
  preferred_countries: string[];
  preferred_locations: string[];
  remote_preference: string;
  min_salary?: number;
  visa_sponsorship_required: boolean;
  desired_employment_types: string[];
  resume_text?: string;
}

export interface JobResult {
  source: string;
  external_id: string;
  title: string;
  company?: string;
  location?: string;
  url?: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  posted_at?: string;
  employment_type?: string;
  match_score?: number;
  match_reason?: string;
}

export interface SavedJob {
  id: string;
  source: string;
  external_id: string;
  title: string;
  company?: string;
  location?: string;
  url?: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  status: string;
  match_score?: number;
  notes?: string;
}

//---new functions for AI cover letter generation
export const uploadResume = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post<Profile>("/profile/resume-upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// ---------- Auth ----------
export const registerUser = (data: { email: string; password: string; full_name?: string }) =>
  api.post<User>("/auth/register", data);

export const loginUser = (data: { email: string; password: string }) =>
  api.post<{ access_token: string }>("/auth/login", data);

export const getMe = () => api.get<User>("/auth/me");
export const loginWithGoogle = (credential: string) =>
  api.post<{ access_token: string }>("/auth/google", { credential });
// ---------- Profile ----------
export const getProfile = () => api.get<Profile>("/profile");
export const updateProfile = (data: Partial<Profile>) => api.put<Profile>("/profile", data);

// ---------- Jobs ----------
export const searchJobs = (params: {
  q: string;
  location?: string;
  country?: string;
  salary_min?: number;
  page?: number;
}) => api.get<JobResult[]>("/jobs/search", { params });

// ---------- Saved jobs ----------
export const listSavedJobs = (status?: string) =>
  api.get<SavedJob[]>("/saved-jobs", { params: status ? { status } : {} });

export const saveJob = (job: Partial<SavedJob>) => api.post<SavedJob>("/saved-jobs", job);

export const updateSavedJob = (id: string, data: { status?: string; notes?: string }) =>
  api.patch<SavedJob>(`/saved-jobs/${id}`, data);

export const deleteSavedJob = (id: string) => api.delete(`/saved-jobs/${id}`);

// ---------- AI ----------
export const generateCoverLetter = (data: {
  job_title: string;
  company: string;
  job_description: string;
  tone?: string;
}) => api.post<{ cover_letter: string }>("/ai/cover-letter", data);

// ---------- Scholarships ----------
export interface ScholarshipResult {
  source: string;
  external_id: string;
  name: string;
  provider?: string;
  country?: string;
  degree_levels: string[];
  fields_of_study: string[];
  funding_type?: string;
  deadline?: string;
  url?: string;
  description?: string;
  match_score?: number;
  match_reason?: string;
}

export interface SavedScholarship {
  id: string;
  source: string;
  external_id: string;
  name: string;
  provider?: string;
  country?: string;
  url?: string;
  description?: string;
  deadline?: string;
  status: string;
  notes?: string;
}

export const searchScholarships = (params: {
  q?: string;
  country?: string;
  degree_level?: string;
  field_of_study?: string;
}) => api.get<ScholarshipResult[]>("/scholarships/search", { params });

export const listSavedScholarships = (status?: string) =>
  api.get<SavedScholarship[]>("/saved-scholarships", { params: status ? { status } : {} });

export const saveScholarship = (scholarship: Partial<SavedScholarship>) =>
  api.post<SavedScholarship>("/saved-scholarships", scholarship);

export const updateSavedScholarship = (id: string, data: { status?: string; notes?: string }) =>
  api.patch<SavedScholarship>(`/saved-scholarships/${id}`, data);

export const deleteSavedScholarship = (id: string) => api.delete(`/saved-scholarships/${id}`);