export interface Resource {
  id: string
  type: string
  region: string
  service: string
  name?: string
  tags: Record<string, string>
  created_time?: string
  state?: string
}

export interface ServiceInfo {
  name: string
  display_name: string
  category: string
  resource_types: string[]
}

export interface DiscoverRequest {
  regions: string[]
  services: string[]
  tags?: string
}

export interface DryRunResponse {
  total_resources: number
  resources_by_service: Record<string, number>
  resources_by_region: Record<string, number>
  resources: Resource[]
  dependencies: any[]
}

export interface DeleteRequest extends DiscoverRequest {
  confirm: boolean
  resources?: string[]
}

export interface DeleteResponse {
  status: string
  deleted_count: number
  failed_count: number
  results: Array<{
    service: string
    region: string
    status: string
    error?: string
  }>
}
