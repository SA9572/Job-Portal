// =============================================
// JOB MODEL TYPES
// =============================================

export interface Job {
  id: number;
  source: string;
  external_id: string;
  title: string;
  excerpt: string | null;
  company: string;
  company_slug: string | null;
  company_logo: string | null;
  employment_type: string | null;
  minimum_salary: number | null;
  maximum_salary: number | null;
  salary_period: string | null;
  currency: string | null;
  seniority: string[];
  location_restrictions: string[];
  timezone_restrictions: string[];
  categories: string[];
  parent_categories: string[];
  description: string;
  published_at: string;
  expires_at: string | null;
  application_url: string;
  source_url: string;
  content_hash: string;
  fetched_at: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  deleted_at: string | null;
  fts_snippet?: string | null;
  relevance_score?: number | null;
  similarity_score?: number;
}

export interface JobListResponse {
  count: number;
  total: number;
  limit: number;
  offset: number;
  jobs: Job[];
}

export interface JobStats {
  total: number;
  active: number;
  expired: number;
  deleted: number;
}

export interface FilterOptions {
  companies: string[];
  employment_types: string[];
  locations: string[];
  seniorities: string[];
  categories: string[];
  currencies: string[];
  min_salary: number | null;
  max_salary: number | null;
}

// =============================================
// USER & AUTH TYPES
// =============================================

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// =============================================
// SAVED JOBS TYPES
// =============================================

export interface SavedJob {
  id: number;
  user_id: number;
  job_id: number;
  notes: string | null;
  created_at: string;
  job: Job;
}

export interface SavedJobListResponse {
  count: number;
  total: number;
  limit: number;
  offset: number;
  jobs: SavedJob[];
}

// =============================================
// JOB ALERT TYPES
// =============================================

export interface JobAlert {
  id: number;
  user_id: number;
  name: string;
  keywords: string | null;
  location: string | null;
  category: string | null;
  seniority: string | null;
  min_salary: number | null;
  frequency: string;
  is_active: boolean;
  last_sent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobAlertListResponse {
  count: number;
  total: number;
  limit: number;
  offset: number;
  alerts: JobAlert[];
}

export interface AlertMatchResponse {
  alert_id: number;
  alert_name: string;
  count: number;
  total: number;
  jobs: Job[];
}

// =============================================
// JOB MATCHING TYPES
// =============================================

export interface UserProfileMatch {
  desired_title?: string;
  skills: string[];
  preferred_locations: string[];
  seniority: string[];
  min_salary?: number;
}

export interface MatchBreakdown {
  title_match: number;
  skill_match: number;
  location_match: number;
  seniority_match: number;
  salary_match: number;
}

export interface MatchedJob extends Job {
  match_score: number;
  match_breakdown: MatchBreakdown;
}

export interface MatchedJobListResponse {
  count: number;
  total: number;
  limit: number;
  offset: number;
  jobs: MatchedJob[];
}

export interface SingleJobMatchResponse {
  job_id: number;
  job_title: string;
  match_score: number;
  match_breakdown: MatchBreakdown;
}

// =============================================
// INGESTION & ADMIN TYPES
// =============================================

export interface IngestionRunResponse {
  run_id: number;
  message: string;
  source: string;
  pages_attempted: number;
  pages_succeeded: number;
  pages_failed: number;
  jobs_fetched: number;
  jobs_valid: number;
  jobs_invalid: number;
  jobs_new: number;
  jobs_duplicate: number;
  jobs_changed: number;
  errors_count: number;
}
