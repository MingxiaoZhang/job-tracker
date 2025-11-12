import { NextResponse } from 'next/server';
import { getRecentJobs } from '@/lib/dynamodb';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get('days') || '30');
    const source = searchParams.get('source');
    const status = searchParams.get('status');
    const workMode = searchParams.get('work_mode');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '25');

    let jobs = await getRecentJobs(days);

    // Apply filters
    if (source) {
      jobs = jobs.filter((job) => job.board_source === source);
    }
    if (status) {
      jobs = jobs.filter((job) => job.status === status);
    }
    if (workMode) {
      jobs = jobs.filter((job) => job.work_mode === workMode);
    }

    // Calculate pagination
    const totalJobs = jobs.length;
    const totalPages = Math.ceil(totalJobs / limit);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedJobs = jobs.slice(startIndex, endIndex);

    return NextResponse.json({
      jobs: paginatedJobs,
      pagination: {
        page,
        limit,
        totalJobs,
        totalPages,
        hasNextPage: page < totalPages,
        hasPreviousPage: page > 1,
      },
    });
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch jobs' },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
export const revalidate = 0;
