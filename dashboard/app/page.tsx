'use client';

import { useEffect, useState } from 'react';
import StatsCards from '@/components/StatsCards';
import Charts from '@/components/Charts';
import JobsTable from '@/components/JobsTable';
import { Stats } from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-purple-700 text-white py-8 px-6 mb-8 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">Job Tracker Dashboard</h1>
          <p className="text-primary-100 text-lg">
            Comprehensive analytics for your job search
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 pb-12">
        {/* Stats Cards */}
        <StatsCards stats={stats} loading={loading} />

        {/* Charts */}
        <div className="mb-8">
          <Charts />
        </div>

        {/* Jobs Table */}
        <JobsTable />
      </div>
    </div>
  );
}
