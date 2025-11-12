import { NextResponse } from 'next/server';
import { getRecentJobs, getJobStats } from '@/lib/dynamodb';

export async function GET() {
  try {
    const jobs = await getRecentJobs(365); // Get all jobs from last year
    const stats = await getJobStats(jobs);

    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
export const revalidate = 0;
