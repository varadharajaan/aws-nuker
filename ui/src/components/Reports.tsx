import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Download, Filter, Calendar, TrendingDown } from 'lucide-react';
import { api } from '../lib/api';
import type { Report, CostSavings } from '../lib/types';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export function Reports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [costSavings, setCostSavings] = useState<CostSavings | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7d');
  const [filterService, setFilterService] = useState('all');

  useEffect(() => {
    loadReports();
  }, [dateRange, filterService]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await api.getReports({ 
        range: dateRange,
        service: filterService === 'all' ? undefined : filterService 
      });
      setReports(data.reports);
      setCostSavings(data.cost_savings);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportReports = (format: 'csv' | 'json' | 'pdf') => {
    const dataStr = format === 'json' 
      ? JSON.stringify(reports, null, 2)
      : reports.map(r => `${r.timestamp},${r.service},${r.region},${r.resource_count},${r.cost_saved}`).join('\n');
    
    const blob = new Blob([dataStr], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aws-nuker-reports.${format}`;
    a.click();
  };

  const aggregateByService = () => {
    const serviceMap: Record<string, number> = {};
    reports.forEach(report => {
      serviceMap[report.service] = (serviceMap[report.service] || 0) + report.resource_count;
    });
    return Object.entries(serviceMap).map(([name, value]) => ({ name, value }));
  };

  const aggregateByCost = () => {
    const serviceMap: Record<string, number> = {};
    reports.forEach(report => {
      serviceMap[report.service] = (serviceMap[report.service] || 0) + report.cost_saved;
    });
    return Object.entries(serviceMap).map(([name, value]) => ({ name, value }));
  };

  const timelineData = reports.map(report => ({
    date: new Date(report.timestamp).toLocaleDateString(),
    resources: report.resource_count,
    cost: report.cost_saved
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Reports & Analytics</h1>
        <div className="flex gap-2">
          <button
            onClick={() => exportReports('csv')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button
            onClick={() => exportReports('json')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={filterService}
              onChange={(e) => setFilterService(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
            >
              <option value="all">All Services</option>
              <option value="ec2">EC2</option>
              <option value="s3">S3</option>
              <option value="rds">RDS</option>
              <option value="lambda">Lambda</option>
              <option value="dynamodb">DynamoDB</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cost Savings Summary */}
      {costSavings && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Savings</p>
                <p className="text-2xl font-bold text-green-600">${costSavings.total_saved.toFixed(2)}</p>
              </div>
              <TrendingDown className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Resources Deleted</p>
                <p className="text-2xl font-bold">{costSavings.resources_deleted}</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Cost/Resource</p>
                <p className="text-2xl font-bold">${(costSavings.total_saved / costSavings.resources_deleted).toFixed(2)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Cleanups Executed</p>
                <p className="text-2xl font-bold">{reports.length}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resource Count by Service */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Resources Deleted by Service</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={aggregateByService()}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {aggregateByService().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Savings by Service */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Cost Savings by Service</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={aggregateByCost()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
              <Legend />
              <Bar dataKey="value" fill="#10B981" name="Cost Saved ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Timeline */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 lg:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Cleanup Timeline</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="resources" stroke="#3B82F6" name="Resources" />
              <Line yAxisId="right" type="monotone" dataKey="cost" stroke="#10B981" name="Cost ($)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cleanup History Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold">Cleanup History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Region
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resources
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cost Saved
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {reports.map((report, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(report.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {report.service.toUpperCase()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {report.region}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {report.resource_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                    ${report.cost_saved.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      report.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : report.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
