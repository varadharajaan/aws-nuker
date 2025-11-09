import axios from 'axios'
import type { DiscoverRequest, DryRunResponse, DeleteRequest, DeleteResponse, ServiceInfo } from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  // Health check
  async healthCheck() {
    const response = await api.get('/')
    return response.data
  },

  // Get available services
  async getServices(): Promise<ServiceInfo[]> {
    const response = await api.get('/api/services')
    return response.data
  },

  // Get available regions
  async getRegions(): Promise<string[]> {
    const response = await api.get('/api/regions')
    return response.data
  },

  // Discover resources
  async discoverResources(request: DiscoverRequest): Promise<DryRunResponse> {
    const response = await api.post('/api/discover', request)
    return response.data
  },

  // Dry run
  async dryRun(request: DiscoverRequest): Promise<DryRunResponse> {
    const response = await api.post('/api/dryrun', request)
    return response.data
  },

  // Delete resources
  async deleteResources(request: DeleteRequest): Promise<DeleteResponse> {
    const response = await api.post('/api/delete', request)
    return response.data
  },

  // Get reports
  async getReports() {
    const response = await api.get('/api/reports')
    return response.data
  },
}
