import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/utils/api'
import { AlertTriangle, Play, Trash2, CheckCircle, XCircle } from 'lucide-react'

export default function DryRunPage() {
  const [selectedRegions, setSelectedRegions] = useState<string[]>([])
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [tagFilter, setTagFilter] = useState('')
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const { data: services } = useQuery({
    queryKey: ['services'],
    queryFn: () => apiClient.getServices(),
  })

  const { data: regions } = useQuery({
    queryKey: ['regions'],
    queryFn: () => apiClient.getRegions(),
  })

  const dryRunMutation = useMutation({
    mutationFn: () =>
      apiClient.dryRun({
        regions: selectedRegions.length > 0 ? selectedRegions : ['us-east-1'],
        services: selectedServices.length > 0 ? selectedServices : ['all'],
        tags: tagFilter || undefined,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: () =>
      apiClient.deleteResources({
        regions: selectedRegions,
        services: selectedServices,
        tags: tagFilter || undefined,
        confirm: true,
      }),
    onSuccess: () => {
      setShowDeleteModal(false)
      // Optionally refetch dry run data
      dryRunMutation.mutate()
    },
  })

  const handleDryRun = () => {
    dryRunMutation.mutate()
  }

  const handleDelete = () => {
    setShowDeleteModal(true)
  }

  const confirmDelete = () => {
    deleteMutation.mutate()
  }

  const groupedServices = services?.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = []
    }
    acc[service.category].push(service)
    return acc
  }, {} as Record<string, typeof services>)

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dry Run & Delete</h1>
        <p className="mt-2 text-gray-400">
          Simulate resource deletion before executing. Review what will be deleted.
        </p>
      </div>

      {/* Warning Banner */}
      <div className="bg-red-900 border border-red-700 rounded-md p-4 mb-8">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-200">Dangerous Operation</h3>
            <div className="mt-2 text-sm text-red-300">
              <p>
                Deletion is permanent and cannot be undone. Always run a dry run first to verify
                what will be deleted. Use with extreme caution in production environments.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Deletion Configuration</h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Regions</label>
            <select
              multiple
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-red-500"
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
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Services</label>
            <select
              multiple
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-red-500"
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
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Tag Filters</label>
            <input
              type="text"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="env=dev,!protected"
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={handleDryRun}
            disabled={dryRunMutation.isPending}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center justify-center gap-2"
          >
            <Play size={16} />
            {dryRunMutation.isPending ? 'Running...' : 'Run Dry Run'}
          </button>

          <button
            onClick={handleDelete}
            disabled={
              !dryRunMutation.data ||
              dryRunMutation.data.total_resources === 0 ||
              deleteMutation.isPending
            }
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center justify-center gap-2"
          >
            <Trash2 size={16} />
            Execute Deletion
          </button>
        </div>
      </div>

      {/* Dry Run Results */}
      {dryRunMutation.data && (
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Dry Run Results</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-400">Total Resources</div>
              <div className="text-2xl font-bold text-white mt-1">
                {dryRunMutation.data.total_resources}
              </div>
            </div>

            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-400">Services Affected</div>
              <div className="text-2xl font-bold text-white mt-1">
                {Object.keys(dryRunMutation.data.resources_by_service).length}
              </div>
            </div>

            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-400">Regions Affected</div>
              <div className="text-2xl font-bold text-white mt-1">
                {Object.keys(dryRunMutation.data.resources_by_region).length}
              </div>
            </div>
          </div>

          {/* Resources Table */}
          {dryRunMutation.data.resources.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700">
                <thead className="bg-gray-750">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Resource ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Region
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      State
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-gray-800 divide-y divide-gray-700">
                  {dryRunMutation.data.resources.map((resource, idx) => (
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Will be deleted
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Deletion Results */}
      {deleteMutation.data && (
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Deletion Results</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-green-900 rounded-lg p-4 border border-green-700">
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-400 mr-2" />
                <div>
                  <div className="text-sm text-green-200">Successfully Deleted</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    {deleteMutation.data.deleted_count}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-red-900 rounded-lg p-4 border border-red-700">
              <div className="flex items-center">
                <XCircle className="h-6 w-6 text-red-400 mr-2" />
                <div>
                  <div className="text-sm text-red-200">Failed</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    {deleteMutation.data.failed_count}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {deleteMutation.data.results.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700">
                <thead className="bg-gray-750">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Service
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Region
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">
                      Error
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-gray-800 divide-y divide-gray-700">
                  {deleteMutation.data.results.map((result, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {result.service}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {result.region}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {result.status === 'completed' ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Completed
                          </span>
                        ) : (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">{result.error || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg max-w-md w-full p-6 border border-gray-700">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-6 w-6 text-red-500 mr-2" />
              <h3 className="text-xl font-bold text-white">Confirm Deletion</h3>
            </div>

            <p className="text-gray-300 mb-6">
              You are about to permanently delete{' '}
              <span className="font-bold text-red-400">{dryRunMutation.data?.total_resources}</span>{' '}
              resources. This action cannot be undone.
            </p>

            <div className="flex gap-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleteMutation.isPending}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
