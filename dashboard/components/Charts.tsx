'use client';

import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartData {
  labels?: string[];
  values?: number[];
  dates?: string[];
  counts?: number[];
  companies?: string[];
  locations?: string[];
  ranges?: string[];
  total_with_salary?: number;
}

function ChartCard({
  title,
  children,
  height = 'h-80',
}: {
  title: string;
  children: React.ReactNode;
  height?: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <div className={`${height} relative`}>
        {children}
      </div>
    </div>
  );
}

export default function Charts() {
  const [sourceData, setSourceData] = useState<ChartData | null>(null);
  const [timelineData, setTimelineData] = useState<ChartData | null>(null);
  const [companiesData, setCompaniesData] = useState<ChartData | null>(null);
  const [locationsData, setLocationsData] = useState<ChartData | null>(null);
  const [jobTypesData, setJobTypesData] = useState<ChartData | null>(null);
  const [workModesData, setWorkModesData] = useState<ChartData | null>(null);
  const [salaryData, setSalaryData] = useState<ChartData | null>(null);

  useEffect(() => {
    fetchChartData();
  }, []);

  const fetchChartData = async () => {
    try {
      const [source, timeline, companies, locations, jobTypes, workModes, salary] =
        await Promise.all([
          fetch('/api/charts/source-distribution').then((r) => r.json()),
          fetch('/api/charts/timeline?days=30').then((r) => r.json()),
          fetch('/api/charts/top-companies?limit=10').then((r) => r.json()),
          fetch('/api/charts/top-locations?limit=10').then((r) => r.json()),
          fetch('/api/charts/job-types').then((r) => r.json()),
          fetch('/api/charts/work-modes').then((r) => r.json()),
          fetch('/api/charts/salary-distribution').then((r) => r.json()),
        ]);

      setSourceData(source);
      setTimelineData(timeline);
      setCompaniesData(companies);
      setLocationsData(locations);
      setJobTypesData(jobTypes);
      setWorkModesData(workModes);
      setSalaryData(salary);
    } catch (error) {
      console.error('Error fetching chart data:', error);
    }
  };

  const colors = {
    primary: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#38f9d7'],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Jobs by Source" height="h-80">
          {sourceData && (
            <Pie
              data={{
                labels: sourceData.labels,
                datasets: [
                  {
                    data: sourceData.values || [],
                    backgroundColor: colors.primary,
                    borderWidth: 2,
                    borderColor: '#fff',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Jobs Posted Over Time (Last 30 Days)" height="h-80">
          {timelineData && (
            <Line
              data={{
                labels: timelineData.dates,
                datasets: [
                  {
                    label: 'Jobs Posted',
                    data: timelineData.counts || [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Top Companies" height="h-96">
          {companiesData && (
            <Bar
              data={{
                labels: companiesData.companies,
                datasets: [
                  {
                    label: 'Jobs',
                    data: companiesData.counts || [],
                    backgroundColor: '#764ba2',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  x: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Top Locations" height="h-96">
          {locationsData && (
            <Bar
              data={{
                labels: locationsData.locations,
                datasets: [
                  {
                    label: 'Jobs',
                    data: locationsData.counts || [],
                    backgroundColor: '#43e97b',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  x: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Job Types" height="h-80">
          {jobTypesData && (
            <Pie
              data={{
                labels: jobTypesData.labels,
                datasets: [
                  {
                    data: jobTypesData.values || [],
                    backgroundColor: colors.primary,
                    borderWidth: 2,
                    borderColor: '#fff',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Work Modes" height="h-80">
          {workModesData && (
            <Bar
              data={{
                labels: workModesData.labels,
                datasets: [
                  {
                    label: 'Jobs',
                    data: workModesData.values || [],
                    backgroundColor: colors.primary,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          )}
        </ChartCard>
      </div>

      <ChartCard title="Salary Distribution" height="h-80">
        {salaryData && salaryData.total_with_salary && salaryData.total_with_salary > 0 ? (
          <>
            <p className="text-sm text-gray-600 mb-2 absolute -top-8 left-0">
              {salaryData.total_with_salary} jobs with salary data
            </p>
            <Bar
              data={{
                labels: salaryData.ranges,
                datasets: [
                  {
                    label: 'Jobs',
                    data: salaryData.counts || [],
                    backgroundColor: '#f093fb',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </>
        ) : (
          <p className="text-center text-gray-500 py-12">No salary data available</p>
        )}
      </ChartCard>
    </div>
  );
}
