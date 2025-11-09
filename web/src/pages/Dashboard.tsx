import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/utils/api'
import { Activity, Server, Globe, Database, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

export default function Dashboard() {
  const [selectedRegions, setSelectedRegions] = useState<string[]>([])
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [tagFilter, setTagFilter] = useState('')

  const { data: services, isLoading: servicesLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => apiClient.getServices(),
  })

  const { data: regions, isLoading: regionsLoading } = useQuery({
    queryKey: ['regions'],
    queryFn: () => apiClient.getRegions(),
  })

  const { data: discoveryData, isLoading: discoveryLoading, refetch } = useQuery({
    queryKey: ['discover', selectedRegions, selectedServices, tagFilter],
    queryFn: () =>
      apiClient.discoverResources({
        regions: selectedRegions.length > 0 ? selectedRegions : ['us-east-1'],
        services: selectedServices.length > 0 ? selectedServices : ['all'],
        tags: tagFilter || undefined,
      }),
    enabled: false, // Manual trigger
  })

  const groupedServices = services?.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = []
    }
    acc[service.category].push(service)
    return acc
  }, {} as Record<string, typeof services>)

  const handleDiscover = () => {
    refetch()
  }

  const serviceChartData = discoveryData?.resources_by_service
    ? Object.entries(discoveryData.resources_by_service).map(([service, count]) => ({
        name: service,
        count,
      }))
    : []

  const regionChartData = discoveryData?.resources_by_region
    ? Object.entries(discoveryData.resources_by_region).map(([region, count]) => ({
        name: region,
        count,
      }))
    : []

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">AWS Nuker Dashboard</h1>
        <p className="mt-2 text-gray-400">
          Discover and manage AWS resources across 67+ services and multiple regions
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-700">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Server className="h-6 w-6 text-blue-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-400 truncate">Total Resources</dt>
                  <dd className="text-lg font-semibold text-white">
                    {discoveryData?.total_resources || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-700">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="h-6 w-6 text-green-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-400 truncate">Services</dt>
                  <dd className="text-lg font-semibold text-white">{services?.length || 67}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-700">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Globe className="h-6 w-6 text-yellow-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-400 truncate">Regions</dt>
                  <dd className="text-lg font-semibold text-white">{regions?.length || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-700">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Database className="h-6 w-6 text-purple-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-400 truncate">Active Filters</dt>
                  <dd className="text-lg font-semibold text-white">
                    {(selectedRegions.length > 0 ? 1 : 0) +
                      (selectedServices.length > 0 ? 1 : 0) +
                      (tagFilter ? 1 : 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Resource Discovery</h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-4">
          {/* Regions */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Regions</label>
            <select
              multiple
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedRegions}
              onChange={(e) =>
                setSelectedRegions(Array.from(e.target.selectedOptions, (option) => option.value))
              }
              size={5}
            >
              {regions?.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-400">Hold Ctrl/Cmd to select multiple</p>
          </div>

          {/* Services */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Services</label>
            <select
              multiple
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedServices}
              onChange={(e) =>
                setSelectedServices(Array.from(e.target.selectedOptions, (option) => option.value))
              }
              size={5}
            >
              {Object.entries(groupedServices || {}).map(([category, categoryServices]) => (
                <optgroup key={category} label={category}>
                  {categoryServices.map((service) => (
                    <option key={service.name} value={service.name}>
                      {service.display_name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-400">Hold Ctrl/Cmd to select multiple</p>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Tag Filters</label>
            <input
              type="text"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="env=dev,owner=*,!protected"
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
            />
            <div className="mt-2 text-xs text-gray-400 space-y-1">
              <p>Examples:</p>
              <p>• env=dev - Exact match</p>
              <p>• owner=john* - Prefix wildcard</p>
              <p>• !protected - Tag must not exist</p>
            </div>
          </div>
        </div>

        <button
          onClick={handleDiscover}
          disabled={discoveryLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          {discoveryLoading ? 'Discovering...' : 'Discover Resources'}
        </button>
      </div>

      {/* Charts */}
      {discoveryData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Resources by Service</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={serviceChartData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" angle={-45} textAnchor="end" height={100} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Resources by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={regionChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {regionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Resources Table */}
      {discoveryData && discoveryData.resources.length > 0 && (
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Discovered Resources</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-750">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Region
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Tags
                  </th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {discoveryData.resources.slice(0, 50).map((resource, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">
                      {resource.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {resource.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {resource.region}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {resource.name || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {Object.entries(resource.tags).length > 0
                        ? Object.entries(resource.tags)
                            .slice(0, 2)
                            .map(([k, v]) => `${k}=${v}`)
                            .join(', ')
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {discoveryData.resources.length > 50 && (
            <div className="px-6 py-4 bg-gray-750 border-t border-gray-700 text-sm text-gray-400">
              Showing 50 of {discoveryData.resources.length} resources
            </div>
          )}
        </div>
      )}

      {/* Warning Alert */}
      {discoveryData && discoveryData.total_resources === 0 && (
        <div className="bg-yellow-900 border border-yellow-700 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-200">No resources found</h3>
              <div className="mt-2 text-sm text-yellow-300">
                <p>
                  No resources were discovered with the current filters. Try adjusting your region,
                  service, or tag selections.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
