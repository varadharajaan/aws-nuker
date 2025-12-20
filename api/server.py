"""
FastAPI backend server for AWS Nuker UI Dashboard.

Provides REST API endpoints for resource discovery, deletion,
dry-run simulation, approvals, and reporting.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path to import aws_nuker modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from aws_nuker.tag_manager import TagManager
    from aws_nuker.policy_templates import PolicyTemplates
    from aws_nuker.approval_gate import ApprovalGate
    from aws_nuker.notification_manager import NotificationManager
    from aws_nuker.config import NukerConfig
except ImportError:
    # Graceful fallback if modules don't exist yet
    TagManager = None
    PolicyTemplates = None
    ApprovalGate = None
    NotificationManager = None
    NukerConfig = None

app = FastAPI(
    title="AWS Nuker API",
    description="REST API for AWS resource cleanup and management",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class DiscoverRequest(BaseModel):
    region: Optional[str] = "us-east-1"
    service: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class FilterRequest(BaseModel):
    tag_key: str
    tag_value: Optional[str] = None
    operator: str = "equals"  # equals, starts_with, contains, regex


class DryRunRequest(BaseModel):
    resource_ids: List[str]
    region: str = "us-east-1"


class DeleteRequest(BaseModel):
    resource_ids: List[str]
    region: str = "us-east-1"
    soft_delete: bool = True
    force: bool = False


class UndoRequest(BaseModel):
    deletion_id: str


class ApprovalActionRequest(BaseModel):
    action: str  # "approve" or "reject"
    comment: Optional[str] = None


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AWS Nuker API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# 1. Discover resources endpoint
@app.get("/api/discover")
async def discover_resources(
    region: str = Query("us-east-1", description="AWS region"),
    service: Optional[str] = Query(None, description="Service to filter by"),
    tag_key: Optional[str] = Query(None, description="Tag key to filter by"),
    tag_value: Optional[str] = Query(None, description="Tag value to filter by")
):
    """
    Discover AWS resources with optional filters.
    
    Returns list of resources matching the specified criteria.
    """
    try:
        # Mock response for demonstration
        resources = [
            {
                "id": "i-1234567890abcdef0",
                "name": "web-server-1",
                "type": "ec2:instance",
                "region": region,
                "tags": {"env": "dev", "project": "webapp"},
                "state": "running",
                "created": "2023-01-15T10:30:00Z",
                "cost_monthly": 45.50
            },
            {
                "id": "vol-0987654321fedcba0",
                "name": "data-volume",
                "type": "ec2:volume",
                "region": region,
                "tags": {"env": "dev", "project": "webapp"},
                "state": "in-use",
                "created": "2023-01-15T10:35:00Z",
                "cost_monthly": 12.30
            }
        ]
        
        # Apply service filter if provided
        if service:
            resources = [r for r in resources if r["type"].startswith(service)]
        
        # Apply tag filter if provided
        if tag_key:
            resources = [r for r in resources if tag_key in r.get("tags", {})]
            if tag_value:
                resources = [r for r in resources if r.get("tags", {}).get(tag_key) == tag_value]
        
        return {
            "count": len(resources),
            "resources": resources,
            "region": region
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. Apply filters endpoint
@app.post("/api/filter")
async def apply_filters(request: FilterRequest):
    """
    Apply complex tag-based filters to discover resources.
    
    Supports pattern matching, regex, and boolean logic.
    """
    try:
        # Mock filtered results
        filtered_resources = [
            {
                "id": "i-1234567890abcdef0",
                "name": "web-server-1",
                "type": "ec2:instance",
                "tags": {request.tag_key: request.tag_value or "dev"},
                "matches_filter": True
            }
        ]
        
        return {
            "filter": request.dict(),
            "matched_count": len(filtered_resources),
            "resources": filtered_resources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. Dry-run simulation endpoint
@app.post("/api/dryrun")
async def dry_run_deletion(request: DryRunRequest):
    """
    Simulate resource deletion without actually deleting.
    
    Returns dependency graph and impact analysis.
    """
    try:
        simulation_result = {
            "resources_to_delete": request.resource_ids,
            "dependencies": [
                {
                    "resource": request.resource_ids[0] if request.resource_ids else "i-123",
                    "depends_on": ["vol-456", "sg-789"],
                    "deletion_order": 1
                }
            ],
            "impact": {
                "total_resources": len(request.resource_ids),
                "total_dependencies": 2,
                "estimated_cost_savings": 57.80,
                "deletion_time_estimate": "2-5 minutes"
            },
            "warnings": [
                "Volume vol-456 is attached and will be detached first",
                "Security group sg-789 has 3 rules that will be deleted"
            ]
        }
        
        return simulation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. Delete resources endpoint
@app.post("/api/delete")
async def delete_resources(request: DeleteRequest):
    """
    Execute resource deletion with optional soft-delete.
    
    Returns deletion status and audit log entry.
    """
    try:
        if not request.force and not request.soft_delete:
            raise HTTPException(
                status_code=400,
                detail="Either force=true or soft_delete=true must be specified"
            )
        
        deletion_result = {
            "deletion_id": "del-20231109-123456",
            "status": "completed" if request.force else "soft_deleted",
            "resources_deleted": len(request.resource_ids),
            "soft_delete_ttl": "7 days" if request.soft_delete else None,
            "audit_log": f"audit/audit_20231109_123456.log",
            "summary": {
                "successful": len(request.resource_ids),
                "failed": 0,
                "skipped": 0
            }
        }
        
        return deletion_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5. Undo/restore endpoint
@app.post("/api/undo")
async def undo_deletion(request: UndoRequest):
    """
    Restore previously deleted resources using rollback snapshots.
    """
    try:
        restore_result = {
            "deletion_id": request.deletion_id,
            "status": "restored",
            "resources_restored": 2,
            "restored_resources": [
                {"id": "i-123", "status": "running"},
                {"id": "vol-456", "status": "available"}
            ]
        }
        
        return restore_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 6. Get reports/audit logs endpoint
@app.get("/api/reports")
async def get_reports(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Fetch audit logs and cleanup reports.
    
    Supports filtering by date range.
    """
    try:
        reports = [
            {
                "id": "rep-001",
                "timestamp": "2023-11-09T12:30:00Z",
                "action": "deletion",
                "resources": 5,
                "cost_saved": 57.80,
                "status": "completed"
            },
            {
                "id": "rep-002",
                "timestamp": "2023-11-08T10:15:00Z",
                "action": "dry_run",
                "resources": 12,
                "cost_saved": 145.20,
                "status": "simulated"
            }
        ]
        
        return {
            "count": len(reports),
            "reports": reports[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 7. List approval requests endpoint
@app.get("/api/approvals")
async def list_approvals(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected")
):
    """
    List cleanup approval requests.
    
    Supports filtering by approval status.
    """
    try:
        approvals = [
            {
                "id": "apr-001",
                "policy": "dev_cleanup",
                "resources": 8,
                "estimated_cost": 150.00,
                "status": "pending",
                "created": "2023-11-09T11:00:00Z",
                "requires_manual_approval": True,
                "reason": "Cost exceeds threshold ($100)"
            },
            {
                "id": "apr-002",
                "policy": "orphan_purge",
                "resources": 3,
                "estimated_cost": 5.50,
                "status": "auto_approved",
                "created": "2023-11-09T09:30:00Z",
                "requires_manual_approval": False
            }
        ]
        
        if status:
            approvals = [a for a in approvals if a["status"] == status]
        
        return {
            "count": len(approvals),
            "approvals": approvals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 8. Approve/reject cleanup endpoint
@app.post("/api/approvals/{approval_id}")
async def process_approval(approval_id: str, request: ApprovalActionRequest):
    """
    Approve or reject a cleanup approval request.
    """
    try:
        if request.action not in ["approve", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
        
        approval_result = {
            "approval_id": approval_id,
            "action": request.action,
            "status": "approved" if request.action == "approve" else "rejected",
            "comment": request.comment,
            "processed_at": "2023-11-09T12:45:00Z"
        }
        
        return approval_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 9. List policy templates endpoint
@app.get("/api/policies")
async def list_policies():
    """
    List available cleanup policy templates.
    """
    try:
        policies = [
            {
                "name": "dev_cleanup",
                "description": "Clean up dev/test/staging environments",
                "tag_filters": ["env=dev", "env=test", "env=staging"],
                "age_threshold": "7 days",
                "approval_threshold": 100.00,
                "soft_delete_ttl": "7 days"
            },
            {
                "name": "orphan_purge",
                "description": "Remove untagged/orphaned resources",
                "tag_filters": ["untagged"],
                "age_threshold": "30 days",
                "approval_threshold": 10.00,
                "soft_delete_ttl": "7 days"
            },
            {
                "name": "cost_kill",
                "description": "Aggressive cost reduction",
                "tag_filters": ["high_cost_unused"],
                "age_threshold": "30 days",
                "approval_threshold": 500.00,
                "soft_delete_ttl": "14 days"
            },
            {
                "name": "storage_cleanup",
                "description": "Clean up large storage resources",
                "tag_filters": ["size>100GB"],
                "age_threshold": "90 days",
                "approval_threshold": 50.00,
                "soft_delete_ttl": None
            }
        ]
        
        return {
            "count": len(policies),
            "policies": policies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 10. Tag discovery endpoint
@app.get("/api/tags")
async def discover_tags(
    region: str = Query("us-east-1"),
    show_untagged: bool = Query(False)
):
    """
    Discover tags across AWS resources.
    
    Optionally show untagged resources.
    """
    try:
        tag_groups = [
            {
                "key": "env",
                "values": ["dev", "test", "staging", "prod"],
                "resource_count": 42
            },
            {
                "key": "project",
                "values": ["webapp", "api", "analytics"],
                "resource_count": 38
            },
            {
                "key": "owner",
                "values": ["team-a", "team-b", "team-c"],
                "resource_count": 35
            }
        ]
        
        result = {
            "tag_groups": tag_groups,
            "total_tags": sum(len(tg["values"]) for tg in tag_groups)
        }
        
        if show_untagged:
            result["untagged_resources"] = {
                "count": 8,
                "resources": [
                    {"id": "i-untagged-1", "type": "ec2:instance"},
                    {"id": "vol-untagged-2", "type": "ec2:volume"}
                ]
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 11. Dashboard statistics endpoint
@app.get("/api/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics and metrics.
    
    Returns resource counts, cost data, and recent activity.
    """
    try:
        stats = {
            "total_resources": 156,
            "resources_by_region": {
                "us-east-1": 89,
                "us-west-2": 45,
                "eu-west-1": 22
            },
            "resources_by_service": {
                "ec2": 45,
                "s3": 28,
                "rds": 12,
                "lambda": 35,
                "dynamodb": 15,
                "other": 21
            },
            "total_monthly_cost": 1245.50,
            "cost_by_service": {
                "ec2": 567.80,
                "rds": 345.20,
                "s3": 123.40,
                "other": 209.10
            },
            "cleanup_candidates": {
                "dev_resources": 42,
                "untagged": 8,
                "aged_resources": 15,
                "potential_savings": 387.90
            },
            "recent_activity": [
                {
                    "action": "deletion",
                    "timestamp": "2023-11-09T12:30:00Z",
                    "resources": 5,
                    "cost_saved": 57.80
                },
                {
                    "action": "dry_run",
                    "timestamp": "2023-11-09T10:15:00Z",
                    "resources": 12,
                    "cost_saved": 145.20
                }
            ]
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("Starting AWS Nuker API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Server: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
