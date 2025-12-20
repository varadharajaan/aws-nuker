# AWS Nuker API Documentation

Complete REST API reference for the AWS Nuker backend server.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

The AWS Nuker API is a RESTful API built with FastAPI that provides programmatic access to all AWS resource cleanup operations.

**Key Features:**
- RESTful architecture
- JSON request/response format
- OpenAPI 3.0 specification
- Auto-generated Swagger UI
- Async/await for performance
- Comprehensive error handling

**Interactive Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Authentication

### Development Mode

In development, authentication is optional. The API accepts requests without auth tokens.

### Production Mode

Production deployments should use JWT authentication.

**Getting a Token:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Using the Token:**
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://localhost:8000/api/discover
```

---

## Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://your-domain.com
```

All API endpoints are prefixed with `/api/`.

---

## Endpoints

### 1. Discover Resources

Discover AWS resources across regions and services with optional filters.

**Endpoint:** `GET /api/discover`

**Query Parameters:**
- `region` (string, optional): AWS region (e.g., "us-east-1")
- `service` (string, optional): Service name (e.g., "ec2")
- `tags` (string, optional): JSON string of tag filters
- `limit` (integer, optional): Max results (default: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

**Request Example:**
```bash
GET /api/discover?region=us-east-1&service=ec2&limit=50
```

**Response Example:**
```json
{
  "total": 245,
  "offset": 0,
  "limit": 50,
  "resources": [
    {
      "id": "i-1234567890abcdef0",
      "type": "ec2:instance",
      "name": "web-server-1",
      "region": "us-east-1",
      "tags": {
        "env": "dev",
        "owner": "john"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "age_days": 45,
      "estimated_cost": 12.34,
      "status": "running"
    }
  ]
}
```

---

### 2. Apply Complex Filters

Apply advanced filtering with boolean logic and pattern matching.

**Endpoint:** `POST /api/filter`

**Request Body:**
```json
{
  "region": "us-east-1",
  "services": ["ec2", "s3"],
  "filters": [
    {
      "type": "tag",
      "key": "env",
      "value": "dev",
      "operator": "equals"
    },
    {
      "type": "age",
      "operator": "greater_than",
      "value": 30
    },
    {
      "type": "cost",
      "operator": "greater_than",
      "value": 100.00
    }
  ],
  "logic": "AND"
}
```

**Response:**
```json
{
  "matched_resources": 24,
  "resources": [...],
  "estimated_savings": 234.56
}
```

---

### 3. Dry-Run Simulation

Simulate deletion to preview impact without executing.

**Endpoint:** `POST /api/dryrun`

**Request Body:**
```json
{
  "resource_ids": [
    "i-1234567890abcdef0",
    "vol-abc123def456"
  ],
  "force": false
}
```

**Response:**
```json
{
  "simulation_id": "sim-xyz789",
  "resources_to_delete": 2,
  "dependencies": [
    {
      "resource_id": "i-1234567890abcdef0",
      "depends_on": ["vol-abc123def456", "sg-xyz789"]
    }
  ],
  "deletion_order": [
    "i-1234567890abcdef0",
    "vol-abc123def456"
  ],
  "warnings": [
    "Security group sg-xyz789 is used by 3 other instances"
  ],
  "estimated_savings": 15.67,
  "estimated_duration": "2m 30s"
}
```

---

### 4. Execute Deletion

Delete resources with optional soft-delete mode.

**Endpoint:** `POST /api/delete`

**Request Body:**
```json
{
  "resource_ids": [
    "i-1234567890abcdef0"
  ],
  "soft_delete": true,
  "retention_days": 7,
  "create_snapshots": true,
  "snapshot_threshold_gb": 10,
  "force": false,
  "dry_run": false
}
```

**Response:**
```json
{
  "operation_id": "op-abc123",
  "status": "in_progress",
  "total_resources": 1,
  "deleted": 0,
  "failed": 0,
  "progress": 0,
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:32:30Z"
}
```

**Check Status:**
```bash
GET /api/operations/{operation_id}
```

---

### 5. Undo Deletion

Restore soft-deleted resources within retention period.

**Endpoint:** `POST /api/undo`

**Request Body:**
```json
{
  "operation_id": "op-abc123"
}
```

**Response:**
```json
{
  "restored": 5,
  "failed": 0,
  "details": [
    {
      "resource_id": "i-1234567890abcdef0",
      "status": "restored",
      "message": "Instance successfully restored"
    }
  ]
}
```

---

### 6. Get Reports

Fetch audit logs and cleanup history.

**Endpoint:** `GET /api/reports`

**Query Parameters:**
- `start_date` (string): ISO 8601 date
- `end_date` (string): ISO 8601 date
- `service` (string, optional): Filter by service
- `region` (string, optional): Filter by region
- `status` (string, optional): success|failed|pending
- `limit` (integer): Max results
- `offset` (integer): Pagination offset

**Request Example:**
```bash
GET /api/reports?start_date=2024-01-01&end_date=2024-01-31&status=success
```

**Response:**
```json
{
  "total": 150,
  "reports": [
    {
      "operation_id": "op-abc123",
      "timestamp": "2024-01-15T10:30:00Z",
      "user": "john@company.com",
      "service": "ec2",
      "region": "us-east-1",
      "resources_deleted": 5,
      "status": "success",
      "cost_savings": 45.67,
      "duration": "2m 15s"
    }
  ]
}
```

---

### 7. List Approval Requests

Get pending and historical approval requests.

**Endpoint:** `GET /api/approvals`

**Query Parameters:**
- `status` (string): pending|approved|rejected|all
- `limit` (integer): Max results
- `offset` (integer): Pagination offset

**Response:**
```json
{
  "total": 5,
  "approvals": [
    {
      "id": "apr-001",
      "policy_name": "dev_cleanup",
      "submitted_by": "john@company.com",
      "submitted_at": "2024-01-15T10:00:00Z",
      "resource_count": 24,
      "estimated_cost": 234.56,
      "status": "pending",
      "auto_approved": false
    }
  ]
}
```

---

### 8. Approve/Reject Request

Make approval decision on a pending request.

**Endpoint:** `POST /api/approvals/{approval_id}`

**Request Body:**
```json
{
  "action": "approve",
  "comment": "Approved after review. Low-value dev resources."
}
```

**Response:**
```json
{
  "approval_id": "apr-001",
  "status": "approved",
  "approved_by": "admin@company.com",
  "approved_at": "2024-01-15T11:00:00Z",
  "comment": "Approved after review. Low-value dev resources."
}
```

---

### 9. List Policies

Get available cleanup policy templates.

**Endpoint:** `GET /api/policies`

**Response:**
```json
{
  "policies": [
    {
      "name": "dev_cleanup",
      "description": "Clean up development/test/staging environments",
      "tag_filters": [
        {"key": "env", "value": "dev|test|staging", "operator": "regex"}
      ],
      "age_threshold_days": 7,
      "approval_threshold": 100.00,
      "soft_delete": true,
      "retention_days": 7,
      "create_snapshots": true,
      "snapshot_threshold_gb": 10
    },
    {
      "name": "orphan_purge",
      "description": "Remove untagged and orphaned resources",
      "tag_filters": [
        {"key": "*", "operator": "not_exists"}
      ],
      "age_threshold_days": 30,
      "approval_threshold": 10.00,
      "soft_delete": true,
      "retention_days": 7
    }
  ]
}
```

---

### 10. Tag Discovery

Discover all tags across resources.

**Endpoint:** `GET /api/tags`

**Query Parameters:**
- `region` (string, optional): Filter by region
- `key` (string, optional): Filter by tag key
- `value` (string, optional): Filter by tag value
- `show_untagged` (boolean): Include untagged resources

**Response:**
```json
{
  "tag_groups": [
    {
      "key": "env",
      "value": "dev",
      "resource_count": 234,
      "estimated_cost": 456.78
    },
    {
      "key": "env",
      "value": "prod",
      "resource_count": 456,
      "estimated_cost": 1234.56
    }
  ],
  "untagged_resources": 45
}
```

---

### 11. Get Statistics

Get dashboard statistics and metrics.

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "total_resources": 12453,
  "estimated_cost": 1234.56,
  "cleanup_candidates": 342,
  "pending_approvals": 5,
  "cost_by_service": {
    "ec2": 456.78,
    "s3": 234.56,
    "rds": 345.67
  },
  "top_services": [
    {"service": "ec2", "count": 1234, "cost": 456.78},
    {"service": "s3", "count": 892, "cost": 234.56}
  ],
  "recent_activity": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "deleted",
      "service": "ec2",
      "count": 5,
      "status": "success"
    }
  ]
}
```

---

## Data Models

### Resource

```typescript
interface Resource {
  id: string;              // AWS resource ID
  type: string;            // e.g., "ec2:instance"
  name: string;            // Resource name
  region: string;          // AWS region
  tags: Record<string, string>;  // Key-value tags
  created_at: string;      // ISO 8601 timestamp
  age_days: number;        // Days since creation
  estimated_cost: number;  // Monthly cost estimate
  status: string;          // Resource status
}
```

### Filter

```typescript
interface Filter {
  type: "tag" | "age" | "cost" | "state" | "owner";
  key?: string;            // For tag filters
  value: string | number;  // Filter value
  operator: "equals" | "contains" | "starts_with" | 
            "greater_than" | "less_than" | "regex" |
            "exists" | "not_exists";
}
```

### TagFilter

```typescript
interface TagFilter {
  key: string;
  value?: string;
  operator: "equals" | "contains" | "starts_with" | 
            "regex" | "exists" | "not_exists";
}
```

### ApprovalRequest

```typescript
interface ApprovalRequest {
  id: string;
  policy_name: string;
  submitted_by: string;
  submitted_at: string;
  resource_count: number;
  estimated_cost: number;
  status: "pending" | "approved" | "rejected";
  auto_approved: boolean;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource i-1234567890 not found",
    "details": {
      "resource_id": "i-1234567890",
      "region": "us-east-1"
    }
  },
  "request_id": "req-abc123"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Temporary unavailable

### Common Error Codes

- `INVALID_PARAMETERS`: Missing or invalid parameters
- `AUTHENTICATION_REQUIRED`: No auth token provided
- `INSUFFICIENT_PERMISSIONS`: IAM permissions lacking
- `RESOURCE_NOT_FOUND`: Specified resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `OPERATION_FAILED`: AWS operation failed
- `DEPENDENCY_EXISTS`: Resource has dependencies
- `REGION_NOT_SUPPORTED`: Invalid AWS region

---

## Rate Limiting

### Limits

- **Unauthenticated**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Premium**: 10000 requests/hour

### Headers

Response headers indicate rate limit status:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642251600
```

### Handling Rate Limits

When rate limit is exceeded (HTTP 429):

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 3600 seconds.",
    "retry_after": 3600
  }
}
```

**Best Practices:**
- Implement exponential backoff
- Cache responses when possible
- Use pagination for large datasets
- Batch operations when supported

---

## Examples

### Example 1: Discover and Delete Dev Resources

```bash
# Step 1: Discover dev resources
curl -X POST http://localhost:8000/api/filter \
  -H "Content-Type: application/json" \
  -d '{
    "region": "us-east-1",
    "services": ["ec2"],
    "filters": [
      {"type": "tag", "key": "env", "value": "dev", "operator": "equals"},
      {"type": "age", "operator": "greater_than", "value": 7}
    ]
  }'

# Step 2: Dry-run to preview
curl -X POST http://localhost:8000/api/dryrun \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["i-123", "i-456"]
  }'

# Step 3: Execute deletion
curl -X POST http://localhost:8000/api/delete \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["i-123", "i-456"],
    "soft_delete": true,
    "retention_days": 7
  }'
```

### Example 2: Approval Workflow

```bash
# Step 1: Submit deletion request (creates approval)
curl -X POST http://localhost:8000/api/delete \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["i-prod-123"],
    "force": false
  }'
# Response: {"approval_id": "apr-001", "status": "pending"}

# Step 2: List pending approvals
curl http://localhost:8000/api/approvals?status=pending

# Step 3: Approve request
curl -X POST http://localhost:8000/api/approvals/apr-001 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comment": "Approved after review"
  }'
```

### Example 3: Generate Cost Report

```bash
# Get cleanup history for last month
curl "http://localhost:8000/api/reports?start_date=2024-01-01&end_date=2024-01-31&status=success"

# Calculate total savings
curl http://localhost:8000/api/stats | jq '.cost_by_service | add'
```

### Example 4: Tag-Based Cleanup

```bash
# Discover untagged resources
curl "http://localhost:8000/api/tags?show_untagged=true"

# Create filter for untagged resources
curl -X POST http://localhost:8000/api/filter \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"type": "tag", "key": "*", "operator": "not_exists"}
    ]
  }'

# Delete untagged resources older than 30 days
curl -X POST http://localhost:8000/api/delete \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["vol-untagged-1", "vol-untagged-2"],
    "soft_delete": true
  }'
```

---

## SDK Examples

### Python

```python
import requests

class AWSNukerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def discover(self, region=None, service=None):
        params = {}
        if region:
            params['region'] = region
        if service:
            params['service'] = service
        
        response = self.session.get(
            f"{self.base_url}/api/discover",
            params=params
        )
        return response.json()
    
    def dry_run(self, resource_ids):
        response = self.session.post(
            f"{self.base_url}/api/dryrun",
            json={"resource_ids": resource_ids}
        )
        return response.json()
    
    def delete(self, resource_ids, soft_delete=True):
        response = self.session.post(
            f"{self.base_url}/api/delete",
            json={
                "resource_ids": resource_ids,
                "soft_delete": soft_delete
            }
        )
        return response.json()

# Usage
client = AWSNukerClient()
resources = client.discover(region="us-east-1", service="ec2")
print(f"Found {len(resources['resources'])} resources")
```

### JavaScript/TypeScript

```typescript
class AWSNukerClient {
  baseUrl: string;

  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async discover(region?: string, service?: string) {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    if (service) params.append('service', service);

    const response = await fetch(
      `${this.baseUrl}/api/discover?${params}`
    );
    return response.json();
  }

  async dryRun(resourceIds: string[]) {
    const response = await fetch(
      `${this.baseUrl}/api/dryrun`,
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({resource_ids: resourceIds})
      }
    );
    return response.json();
  }

  async delete(resourceIds: string[], softDelete = true) {
    const response = await fetch(
      `${this.baseUrl}/api/delete`,
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          resource_ids: resourceIds,
          soft_delete: softDelete
        })
      }
    );
    return response.json();
  }
}

// Usage
const client = new AWSNukerClient();
const resources = await client.discover("us-east-1", "ec2");
console.log(`Found ${resources.total} resources`);
```

---

**End of API Documentation**

For UI guide, see `UI_DASHBOARD_GUIDE.md`  
For deployment, see `DEPLOYMENT_GUIDE.md`  
For architecture, see `ARCHITECTURE_DIAGRAMS.md`
