'use client';

import { useState, useEffect } from 'react';
import { Job } from '@/lib/types';
import { format } from 'date-fns';

interface PaginationInfo {
  page: number;
  limit: number;
  totalJobs: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export default function JobsTable() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 25,
    totalJobs: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPreviousPage: false,
  });
  const [filters, setFilters] = useState({
    days: '30',
    source: '',
    status: '',
    workMode: '',
  });

  useEffect(() => {
    fetchJobs();
  }, [filters, pagination.page]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        days: filters.days,
        page: pagination.page.toString(),
        limit: pagination.limit.toString(),
        ...(filters.source && { source: filters.source }),
        ...(filters.status && { status: filters.status }),
        ...(filters.workMode && { work_mode: filters.workMode }),
      });

      const response = await fetch(`/api/jobs?${params}`);
      const data = await response.json();
      setJobs(data.jobs);
      setPagination((prev) => ({ ...prev, ...data.pagination }));
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFiltersChange = (newFilters: Partial<typeof filters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPagination((prev) => ({ ...prev, page: 1 })); // Reset to page 1 on filter change
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return 'N/A';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Recent Jobs</h2>

      {/* Stats and Filters */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div className="text-sm text-gray-600">
          Showing <span className="font-semibold">{(pagination.page - 1) * pagination.limit + 1}</span> to{' '}
          <span className="font-semibold">{Math.min(pagination.page * pagination.limit, pagination.totalJobs)}</span> of{' '}
          <span className="font-semibold">{pagination.totalJobs}</span> jobs
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-1">Time Period</label>
            <select
              value={filters.days}
              onChange={(e) => handleFiltersChange({ days: e.target.value })}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="7">Last 7 days</option>
              <option value="14">Last 14 days</option>
              <option value="30">Last 30 days</option>
              <option value="60">Last 60 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">All time</option>
            </select>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-1">Source</label>
            <select
              value={filters.source}
              onChange={(e) => handleFiltersChange({ source: e.target.value })}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All sources</option>
              <option value="indeed">Indeed</option>
              <option value="linkedin">LinkedIn</option>
            </select>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFiltersChange({ status: e.target.value })}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-1">Work Mode</label>
            <select
              value={filters.workMode}
              onChange={(e) => handleFiltersChange({ workMode: e.target.value })}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All modes</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="On-site">On-site</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading jobs...</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Work Mode
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Posted
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {jobs.map((job) => (
                  <tr key={job.url} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-800 font-medium"
                      >
                        {job.title}
                      </a>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{job.company}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{job.location || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className="px-2 py-1 bg-gray-100 rounded-full text-gray-800">
                        {job.board_source}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{job.job_type || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{job.work_mode || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(job.posted_date)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {jobs.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No jobs found matching your filters.
              </div>
            )}
          </div>

          {/* Pagination */}
          {jobs.length > 0 && (
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between border-t border-gray-200 pt-4 gap-4">
              {/* Previous/Next buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={!pagination.hasPreviousPage}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={!pagination.hasNextPage}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>

              {/* Page info */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-700">
                  Page <span className="font-medium">{pagination.page}</span> of{' '}
                  <span className="font-medium">{pagination.totalPages}</span>
                </span>
              </div>

              {/* Page numbers */}
              <div className="flex items-center gap-1">
                {/* First page */}
                {pagination.page > 2 && (
                  <>
                    <button
                      onClick={() => handlePageChange(1)}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      1
                    </button>
                    {pagination.page > 3 && (
                      <span className="px-2 text-gray-500">...</span>
                    )}
                  </>
                )}

                {/* Previous page */}
                {pagination.hasPreviousPage && (
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    {pagination.page - 1}
                  </button>
                )}

                {/* Current page */}
                <button
                  className="px-3 py-1 border-2 border-primary-500 bg-primary-50 rounded-md text-sm text-primary-700 font-medium"
                  disabled
                >
                  {pagination.page}
                </button>

                {/* Next page */}
                {pagination.hasNextPage && (
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    {pagination.page + 1}
                  </button>
                )}

                {/* Last page */}
                {pagination.page < pagination.totalPages - 1 && (
                  <>
                    {pagination.page < pagination.totalPages - 2 && (
                      <span className="px-2 text-gray-500">...</span>
                    )}
                    <button
                      onClick={() => handlePageChange(pagination.totalPages)}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      {pagination.totalPages}
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
