import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Trash2, RefreshCw, Tag } from 'lucide-react';
import { useStore } from '../lib/store';
import { api } from '../lib/api';
import { Resource } from '../lib/types';
import { formatCost, formatDate } from '../lib/utils';

interface ResourceExplorerProps {
  onSelectResources?: (resources: Resource[]) => void;
}

export const ResourceExplorer: React.FC<ResourceExplorerProps> = ({ onSelectResources }) => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [filteredResources, setFilteredResources] = useState<Resource[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [regionFilter, setRegionFilter] = useState('all');
  const [serviceFilter, setServiceFilter] = useState('all');
  const [sortBy, setSortBy] = useState<'name' | 'cost' | 'created'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const { filters } = useStore();

  useEffect(() => {
    loadResources();
  }, [filters]);

  useEffect(() => {
    filterAndSortResources();
  }, [resources, searchTerm, regionFilter, serviceFilter, sortBy, sortOrder]);

  const loadResources = async () => {
    setLoading(true);
    try {
      const response = await api.discover({
        ...filters,
        include_tags: true,
      });
      setResources(response.data.resources || []);
    } catch (error) {
      console.error('Failed to load resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortResources = () => {
    let filtered = [...resources];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(r =>
        r.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        Object.values(r.tags || {}).some(v => 
          v.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Region filter
    if (regionFilter !== 'all') {
      filtered = filtered.filter(r => r.region === regionFilter);
    }

    // Service filter
    if (serviceFilter !== 'all') {
      filtered = filtered.filter(r => r.type === serviceFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.id.localeCompare(b.id);
          break;
        case 'cost':
          comparison = (a.cost || 0) - (b.cost || 0);
          break;
        case 'created':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredResources(filtered);
  };

  const toggleSelection = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
    
    if (onSelectResources) {
      const selectedResources = resources.filter(r => newSelected.has(r.id));
      onSelectResources(selectedResources);
    }
  };

  const selectAll = () => {
    const allIds = new Set(filteredResources.map(r => r.id));
    setSelectedIds(allIds);
    if (onSelectResources) {
      onSelectResources(filteredResources);
    }
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
    if (onSelectResources) {
      onSelectResources([]);
    }
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Type', 'Region', 'Cost', 'Created', 'Tags'];
    const rows = filteredResources.map(r => [
      r.id,
      r.type,
      r.region,
      r.cost?.toString() || '0',
      r.created_at,
      JSON.stringify(r.tags || {})
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resources-${new Date().toISOString()}.csv`;
    a.click();
  };

  const uniqueRegions = [...new Set(resources.map(r => r.region))];
  const uniqueServices = [...new Set(resources.map(r => r.type))];

  const paginatedResources = filteredResources.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const totalPages = Math.ceil(filteredResources.length / itemsPerPage);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Resource Explorer</h2>
          <p className="text-gray-500 dark:text-gray-400">
            {filteredResources.length} resources found
            {selectedIds.size > 0 && ` · ${selectedIds.size} selected`}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadResources}
            disabled={loading}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={exportToCSV}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>

        <select
          value={regionFilter}
          onChange={(e) => setRegionFilter(e.target.value)}
          className="input"
        >
          <option value="all">All Regions</option>
          {uniqueRegions.map(region => (
            <option key={region} value={region}>{region}</option>
          ))}
        </select>

        <select
          value={serviceFilter}
          onChange={(e) => setServiceFilter(e.target.value)}
          className="input"
        >
          <option value="all">All Services</option>
          {uniqueServices.map(service => (
            <option key={service} value={service}>{service}</option>
          ))}
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="input"
        >
          <option value="name">Sort by Name</option>
          <option value="cost">Sort by Cost</option>
          <option value="created">Sort by Created</option>
        </select>
      </div>

      {/* Bulk Actions */}
      {selectedIds.size > 0 && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-center justify-between">
          <span className="text-blue-900 dark:text-blue-100 font-medium">
            {selectedIds.size} resource{selectedIds.size > 1 ? 's' : ''} selected
          </span>
          <div className="flex gap-2">
            <button onClick={clearSelection} className="btn btn-sm btn-secondary">
              Clear Selection
            </button>
            <button className="btn btn-sm btn-danger flex items-center gap-2">
              <Trash2 className="w-4 h-4" />
              Delete Selected
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === filteredResources.length && filteredResources.length > 0}
                    onChange={() => selectedIds.size === filteredResources.length ? clearSelection() : selectAll()}
                    className="checkbox"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Resource ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Region
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Tags
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2" />
                    Loading resources...
                  </td>
                </tr>
              ) : paginatedResources.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    No resources found
                  </td>
                </tr>
              ) : (
                paginatedResources.map((resource) => (
                  <tr key={resource.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(resource.id)}
                        onChange={() => toggleSelection(resource.id)}
                        className="checkbox"
                      />
                    </td>
                    <td className="px-4 py-3 text-sm font-mono">{resource.id}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                        {resource.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{resource.region}</td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(resource.tags || {}).slice(0, 2).map(([key, value]) => (
                          <span
                            key={key}
                            className="px-2 py-1 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded text-xs flex items-center gap-1"
                          >
                            <Tag className="w-3 h-3" />
                            {key}={value}
                          </span>
                        ))}
                        {Object.keys(resource.tags || {}).length > 2 && (
                          <span className="text-xs text-gray-500">
                            +{Object.keys(resource.tags || {}).length - 2} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm font-medium">{formatCost(resource.cost || 0)}/mo</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{formatDate(resource.created_at)}</td>
                    <td className="px-4 py-3 text-sm">
                      <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredResources.length)} of {filteredResources.length} results
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="btn btn-sm btn-secondary"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-700 dark:text-gray-300">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="btn btn-sm btn-secondary"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourceExplorer;
