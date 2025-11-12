export interface Job {
  url: string;
  id?: number;
  title: string;
  company: string;
  location?: string;
  board_source: string;
  posted_date?: string;
  status: string;
  job_type?: string;
  work_mode?: string;
  experience_level?: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary_period?: string;
  created_at?: string;
  updated_at?: string;
  applied?: boolean;
  applied_date?: string;
  application_status?: string;
}

export interface Stats {
  total_jobs: number;
  jobs_today: number;
  jobs_this_week: number;
  jobs_this_month: number;
  applied_count: number;
  status_counts: Record<string, number>;
  source_counts: Record<string, number>;
  application_status_counts: Record<string, number>;
}
