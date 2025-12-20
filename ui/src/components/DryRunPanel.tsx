import React, { useState } from 'react';
import { AlertTriangle, Check, X, Download, RefreshCw } from 'lucide-react';

interface Resource {
  id: string;
  type: string;
  region: string;
  name?: string;
  tags: Record<string, string>;
  dependencies: string[];
}

interface DryRunResult {
  resources: Resource[];
  total_resources: number;
  total_cost: number;
  dependencies: Record<string, string[]>;
  warnings: string[];
}

interface DryRunPanelProps {
  selectedResources: Resource[];
  onExecute: () => void;
  onCancel: () => void;
}

export const DryRunPanel: React.FC<DryRunPanelProps> = ({
  selectedResources,
  onExecute,
  onCancel,
}) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DryRunResult | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/dryrun', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resource_ids: selectedResources.map((r) => r.id),
        }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Dry-run failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportResults = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dryrun-${Date.now()}.json`;
    a.click();
  };

  const handleExecute = () => {
    setShowConfirm(true);
  };

  const confirmExecution = () => {
    onExecute();
    setShowConfirm(false);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <AlertTriangle className="mr-2 text-yellow-500" size={24} />
          Dry-Run Simulation
        </h2>
        <div className="flex gap-2">
          <button
            onClick={runSimulation}
            disabled={loading || selectedResources.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <>
                <RefreshCw className="animate-spin mr-2" size={16} />
                Running...
              </>
            ) : (
              'Run Simulation'
            )}
          </button>
          {result && (
            <button
              onClick={exportResults}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center"
            >
              <Download className="mr-2" size={16} />
              Export
            </button>
          )}
        </div>
      </div>

      {selectedResources.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No resources selected. Please select resources from the Resource Explorer.
        </div>
      )}

      {selectedResources.length > 0 && !result && !loading && (
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto mb-4 text-yellow-500" size={48} />
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {selectedResources.length} resources selected for simulation
          </p>
          <p className="text-sm text-gray-500">
            Click "Run Simulation" to preview deletion impact
          </p>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Resources
              </h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {result.total_resources}
              </p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Estimated Cost Savings
              </h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                ${result.total_cost.toFixed(2)}/month
              </p>
            </div>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Dependencies
              </h3>
              <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                {Object.keys(result.dependencies).length}
              </p>
            </div>
          </div>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <h3 className="font-bold text-yellow-800 dark:text-yellow-200 mb-2 flex items-center">
                <AlertTriangle className="mr-2" size={20} />
                Warnings ({result.warnings.length})
              </h3>
              <ul className="list-disc list-inside space-y-1">
                {result.warnings.map((warning, idx) => (
                  <li key={idx} className="text-sm text-yellow-700 dark:text-yellow-300">
                    {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Resources Table */}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-3">
              Resources to be Deleted
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Resource ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Region
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Dependencies
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {result.resources.map((resource) => (
                    <tr key={resource.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {resource.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {resource.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {resource.region}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {resource.dependencies.length > 0 ? (
                          <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-xs">
                            {resource.dependencies.length} deps
                          </span>
                        ) : (
                          <span className="text-gray-400">None</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Dependency Graph */}
          {Object.keys(result.dependencies).length > 0 && (
            <div>
              <h3 className="font-bold text-gray-900 dark:text-white mb-3">
                Dependency Graph
              </h3>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                {Object.entries(result.dependencies).map(([resource, deps]) => (
                  <div key={resource} className="mb-3 last:mb-0">
                    <div className="font-mono text-sm text-gray-900 dark:text-white">
                      {resource}
                    </div>
                    {deps.length > 0 && (
                      <div className="ml-4 mt-1 space-y-1">
                        {deps.map((dep, idx) => (
                          <div
                            key={idx}
                            className="font-mono text-xs text-gray-600 dark:text-gray-400"
                          >
                            ↳ {dep}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onCancel}
              className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center"
            >
              <X className="mr-2" size={16} />
              Cancel
            </button>
            <button
              onClick={handleExecute}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center"
            >
              <Check className="mr-2" size={16} />
              Execute Deletion
            </button>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Confirm Deletion
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Are you sure you want to delete {result?.total_resources} resources? This action cannot be
              undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={confirmExecution}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
