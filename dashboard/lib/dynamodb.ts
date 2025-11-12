import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, ScanCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
  },
});

const docClient = DynamoDBDocumentClient.from(client);

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

const TABLE_NAME = process.env.DYNAMODB_TABLE_NAME || 'job-tracker-jobs';

export async function getAllJobs(): Promise<Job[]> {
  try {
    const command = new ScanCommand({
      TableName: TABLE_NAME,
    });

    const response = await docClient.send(command);
    return (response.Items as Job[]) || [];
  } catch (error) {
    console.error('Error fetching jobs:', error);
    throw error;
  }
}

export async function getRecentJobs(days: number = 30): Promise<Job[]> {
  try {
    const allJobs = await getAllJobs();
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return allJobs.filter((job) => {
      if (!job.posted_date) return false;
      const postedDate = new Date(job.posted_date);
      return postedDate >= cutoffDate;
    });
  } catch (error) {
    console.error('Error fetching recent jobs:', error);
    throw error;
  }
}

export async function getJobStats(jobs: Job[]) {
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const weekStart = new Date(todayStart);
  weekStart.setDate(weekStart.getDate() - weekStart.getDay());
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  let jobsToday = 0;
  let jobsThisWeek = 0;
  let jobsThisMonth = 0;
  let appliedCount = 0;

  const statusCounts: Record<string, number> = {};
  const sourceCounts: Record<string, number> = {};
  const applicationStatusCounts: Record<string, number> = {};

  jobs.forEach((job) => {
    // Time-based stats
    if (job.posted_date) {
      const postedDate = new Date(job.posted_date);
      if (postedDate >= todayStart) jobsToday++;
      if (postedDate >= weekStart) jobsThisWeek++;
      if (postedDate >= monthStart) jobsThisMonth++;
    }

    // Status counts
    const status = job.status || 'unknown';
    statusCounts[status] = (statusCounts[status] || 0) + 1;

    // Source counts
    const source = job.board_source || 'unknown';
    sourceCounts[source] = (sourceCounts[source] || 0) + 1;

    // Application tracking
    if (job.applied) appliedCount++;
    const appStatus = job.application_status || 'not_applied';
    applicationStatusCounts[appStatus] = (applicationStatusCounts[appStatus] || 0) + 1;
  });

  return {
    total_jobs: jobs.length,
    jobs_today: jobsToday,
    jobs_this_week: jobsThisWeek,
    jobs_this_month: jobsThisMonth,
    applied_count: appliedCount,
    status_counts: statusCounts,
    source_counts: sourceCounts,
    application_status_counts: applicationStatusCounts,
  };
}

export async function getTopCompanies(jobs: Job[], limit: number = 10) {
  const companyCounts: Record<string, number> = {};

  jobs.forEach((job) => {
    if (job.company) {
      companyCounts[job.company] = (companyCounts[job.company] || 0) + 1;
    }
  });

  const sorted = Object.entries(companyCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit);

  return {
    companies: sorted.map(([company]) => company),
    counts: sorted.map(([, count]) => count),
  };
}

export async function getTopLocations(jobs: Job[], limit: number = 10) {
  const locationCounts: Record<string, number> = {};

  jobs.forEach((job) => {
    if (job.location) {
      locationCounts[job.location] = (locationCounts[job.location] || 0) + 1;
    }
  });

  const sorted = Object.entries(locationCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit);

  return {
    locations: sorted.map(([location]) => location),
    counts: sorted.map(([, count]) => count),
  };
}

export async function getTimeline(jobs: Job[], days: number = 30) {
  const dateCounts: Record<string, number> = {};

  jobs.forEach((job) => {
    if (job.posted_date) {
      const date = new Date(job.posted_date);
      const dateKey = date.toISOString().split('T')[0];
      dateCounts[dateKey] = (dateCounts[dateKey] || 0) + 1;
    }
  });

  const sortedDates = Object.keys(dateCounts).sort();

  return {
    dates: sortedDates,
    counts: sortedDates.map((date) => dateCounts[date]),
  };
}
