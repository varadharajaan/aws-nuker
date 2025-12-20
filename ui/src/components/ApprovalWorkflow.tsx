import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, DollarSign, AlertCircle } from 'lucide-react';

interface ApprovalRequest {
  id: string;
  policy_name: string;
  resources: Array<{ id: string; type: string; region: string }>;
  estimated_cost: number;
  requested_by: string;
  requested_at: string;
  status: 'pending' | 'approved' | 'rejected';
  auto_approved: boolean;
  comments?: string;
}

export const ApprovalWorkflow: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [comment, setComment] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('pending');

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/approvals');
      const data = await response.json();
      setApprovals(data.approvals || []);
    } catch (error) {
      console.error('Failed to fetch approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/approvals/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'approve', comment }),
      });
      setComment('');
      setSelectedApproval(null);
      fetchApprovals();
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/approvals/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reject', comment }),
      });
      setComment('');
      setSelectedApproval(null);
      fetchApprovals();
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  const filteredApprovals = approvals.filter((approval) =>
    filter === 'all' ? true : approval.status === filter
  );

  const getStatusBadge = (status: string, autoApproved: boolean) => {
    if (autoApproved) {
      return (
        <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-xs font-medium flex items-center">
          <CheckCircle className="mr-1" size={14} />
          Auto-Approved
        </span>
      );
    }
    switch (status) {
      case 'pending':
        return (
          <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-xs font-medium flex items-center">
            <Clock className="mr-1" size={14} />
            Pending
          </span>
        );
      case 'approved':
        return (
          <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-xs font-medium flex items-center">
            <CheckCircle className="mr-1" size={14} />
            Approved
          </span>
        );
      case 'rejected':
        return (
          <span className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-xs font-medium flex items-center">
            <XCircle className="mr-1" size={14} />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <CheckCircle className="mr-2 text-green-500" size={24} />
          Approval Workflow
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            All ({approvals.length})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-md ${
              filter === 'pending'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Pending ({approvals.filter((a) => a.status === 'pending').length})
          </button>
          <button
            onClick={() => setFilter('approved')}
            className={`px-4 py-2 rounded-md ${
              filter === 'approved'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Approved ({approvals.filter((a) => a.status === 'approved').length})
          </button>
          <button
            onClick={() => setFilter('rejected')}
            className={`px-4 py-2 rounded-md ${
              filter === 'rejected'
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Rejected ({approvals.filter((a) => a.status === 'rejected').length})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading approvals...</div>
      ) : filteredApprovals.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No {filter !== 'all' ? filter : ''} approval requests found.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredApprovals.map((approval) => (
            <div
              key={approval.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-bold text-gray-900 dark:text-white">
                      {approval.policy_name}
                    </h3>
                    {getStatusBadge(approval.status, approval.auto_approved)}
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                    <div>
                      <span className="font-medium">Requested by:</span> {approval.requested_by}
                    </div>
                    <div>
                      <span className="font-medium">Requested at:</span>{' '}
                      {new Date(approval.requested_at).toLocaleString()}
                    </div>
                    <div className="flex items-center">
                      <DollarSign size={14} className="mr-1" />
                      <span className="font-medium">Estimated cost:</span>{' '}
                      <span className="ml-1 text-red-600 dark:text-red-400 font-bold">
                        ${approval.estimated_cost.toFixed(2)}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Resources:</span> {approval.resources.length}
                    </div>
                  </div>
                  {approval.comments && (
                    <div className="bg-gray-100 dark:bg-gray-700 rounded p-3 text-sm text-gray-700 dark:text-gray-300">
                      <strong>Comments:</strong> {approval.comments}
                    </div>
                  )}
                </div>
                {approval.status === 'pending' && (
                  <div className="ml-4 flex gap-2">
                    <button
                      onClick={() => setSelectedApproval(approval)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Review
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Approval Modal */}
      {selectedApproval && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Review Approval Request
            </h3>
            
            <div className="space-y-4 mb-6">
              <div>
                <h4 className="font-bold text-gray-700 dark:text-gray-300 mb-2">
                  Policy: {selectedApproval.policy_name}
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Requested by:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {selectedApproval.requested_by}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Estimated cost:</span>
                    <p className="font-bold text-red-600 dark:text-red-400">
                      ${selectedApproval.estimated_cost.toFixed(2)}/month
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-gray-700 dark:text-gray-300 mb-2">
                  Resources ({selectedApproval.resources.length})
                </h4>
                <div className="bg-gray-50 dark:bg-gray-900 rounded p-3 max-h-48 overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left py-2 text-gray-600 dark:text-gray-400">ID</th>
                        <th className="text-left py-2 text-gray-600 dark:text-gray-400">Type</th>
                        <th className="text-left py-2 text-gray-600 dark:text-gray-400">Region</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedApproval.resources.map((resource, idx) => (
                        <tr key={idx} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-2 font-mono text-xs text-gray-900 dark:text-white">
                            {resource.id}
                          </td>
                          <td className="py-2 text-gray-700 dark:text-gray-300">{resource.type}</td>
                          <td className="py-2 text-gray-700 dark:text-gray-300">{resource.region}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <label className="block font-bold text-gray-700 dark:text-gray-300 mb-2">
                  Comments (optional)
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  rows={3}
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setSelectedApproval(null);
                  setComment('');
                }}
                className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={() => handleReject(selectedApproval.id)}
                className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center"
              >
                <XCircle className="mr-2" size={16} />
                Reject
              </button>
              <button
                onClick={() => handleApprove(selectedApproval.id)}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center"
              >
                <CheckCircle className="mr-2" size={16} />
                Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
