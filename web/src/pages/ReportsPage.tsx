import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/utils/api'
import { FileText, Download } from 'lucide-react'

export default function ReportsPage() {
  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => apiClient.getReports(),
  })

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Audit Reports</h1>
        <p className="mt-2 text-gray-400">
          View cleanup history, audit logs, and cost savings reports
        </p>
      </div>

      {isLoading ? (
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-8 text-center">
          <div className="text-gray-400">Loading reports...</div>
        </div>
      ) : reports && reports.length > 0 ? (
        <div className="space-y-4">
          {reports.map((report: any, idx: number) => (
            <div
              key={idx}
              className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6 flex items-center justify-between"
            >
              <div className="flex items-center">
                <FileText className="h-6 w-6 text-blue-500 mr-4" />
                <div>
                  <h3 className="text-lg font-medium text-white">{report.title}</h3>
                  <p className="text-sm text-gray-400">{report.description}</p>
                </div>
              </div>
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center gap-2">
                <Download size={16} />
                Export
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-8 text-center">
          <FileText className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No reports available</h3>
          <p className="text-gray-400">
            Reports will appear here after you run resource cleanup operations.
          </p>
        </div>
      )}

      {/* Placeholder sections */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Cost Savings</h3>
          <div className="text-center py-8">
            <div className="text-4xl font-bold text-green-500 mb-2">$0</div>
            <div className="text-gray-400">Estimated monthly savings</div>
          </div>
        </div>

        <div className="bg-gray-800 shadow rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
          <div className="text-center py-8">
            <div className="text-gray-400">No recent cleanup operations</div>
          </div>
        </div>
      </div>
    </div>
  )
}
