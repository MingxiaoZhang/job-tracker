import { NextResponse } from 'next/server';
import { getRecentJobs, getTopCompanies, getTopLocations, getTimeline } from '@/lib/dynamodb';

export async function GET(
  request: Request,
  { params }: { params: { type: string } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get('days') || '90');
    const limit = parseInt(searchParams.get('limit') || '10');

    const jobs = await getRecentJobs(days);

    switch (params.type) {
      case 'source-distribution': {
        const sourceCounts: Record<string, number> = {};
        jobs.forEach((job) => {
          const source = job.board_source || 'unknown';
          sourceCounts[source] = (sourceCounts[source] || 0) + 1;
        });
        return NextResponse.json({
          labels: Object.keys(sourceCounts),
          values: Object.values(sourceCounts),
        });
      }

      case 'timeline': {
        const timeline = await getTimeline(jobs, days);
        return NextResponse.json(timeline);
      }

      case 'top-companies': {
        const companies = await getTopCompanies(jobs, limit);
        return NextResponse.json(companies);
      }

      case 'top-locations': {
        const locations = await getTopLocations(jobs, limit);
        return NextResponse.json(locations);
      }

      case 'job-types': {
        const typeCounts: Record<string, number> = {};
        jobs.forEach((job) => {
          const type = job.job_type || 'Not specified';
          typeCounts[type] = (typeCounts[type] || 0) + 1;
        });
        return NextResponse.json({
          labels: Object.keys(typeCounts),
          values: Object.values(typeCounts),
        });
      }

      case 'work-modes': {
        const modeCounts: Record<string, number> = {};
        jobs.forEach((job) => {
          const mode = job.work_mode || 'Not specified';
          modeCounts[mode] = (modeCounts[mode] || 0) + 1;
        });
        return NextResponse.json({
          labels: Object.keys(modeCounts),
          values: Object.values(modeCounts),
        });
      }

      case 'salary-distribution': {
        const salaries: number[] = [];
        jobs.forEach((job) => {
          if (job.salary_min && job.salary_max) {
            salaries.push((job.salary_min + job.salary_max) / 2);
          } else if (job.salary_min) {
            salaries.push(job.salary_min);
          } else if (job.salary_max) {
            salaries.push(job.salary_max);
          }
        });

        const ranges = ['<50k', '50-75k', '75-100k', '100-125k', '125-150k', '150-200k', '200k+'];
        const counts = [0, 0, 0, 0, 0, 0, 0];

        salaries.forEach((salary) => {
          if (salary < 50000) counts[0]++;
          else if (salary < 75000) counts[1]++;
          else if (salary < 100000) counts[2]++;
          else if (salary < 125000) counts[3]++;
          else if (salary < 150000) counts[4]++;
          else if (salary < 200000) counts[5]++;
          else counts[6]++;
        });

        return NextResponse.json({
          ranges,
          counts,
          total_with_salary: salaries.length,
        });
      }

      default:
        return NextResponse.json(
          { error: 'Invalid chart type' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Error fetching chart data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch chart data' },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
export const revalidate = 0;
