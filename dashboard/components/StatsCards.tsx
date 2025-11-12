'use client';

import { Stats } from '@/lib/types';

interface StatsCardsProps {
  stats: Stats | null;
  loading: boolean;
}

export default function StatsCards({ stats, loading }: StatsCardsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) return null;

  const cards = [
    { label: 'Total Jobs', value: stats.total_jobs, color: 'text-primary-600' },
    { label: 'This Week', value: stats.jobs_this_week, color: 'text-blue-600' },
    { label: 'This Month', value: stats.jobs_this_month, color: 'text-purple-600' },
    { label: 'Today', value: stats.jobs_today, color: 'text-green-600' },
    { label: 'Applied', value: stats.applied_count, color: 'text-orange-600' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
      {cards.map((card, i) => (
        <div
          key={i}
          className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
        >
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            {card.label}
          </h3>
          <p className={`text-4xl font-bold ${card.color}`}>
            {card.value.toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}
