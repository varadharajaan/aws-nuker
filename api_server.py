#!/usr/bin/env python3
"""
AWS Nuker API Server
FastAPI backend providing REST API for the web dashboard
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
from aws_nuker.services import get_all_services
from aws_nuker.utils import parse_regions, parse_tag_filters, resource_matches_filters
from aws_nuker.cost_estimator import CostEstimator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AWS Nuker API",
    description="API for AWS resource cleanup and management across 67+ services",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class DiscoverRequest(BaseModel):
    regions: List[str]
    services: List[str]
    tags: Optional[str] = None

class DryRunRequest(BaseModel):
    regions: List[str]
    services: List[str]
    tags: Optional[str] = None
    resources: Optional[List[str]] = None

class DeleteRequest(BaseModel):
    regions: List[str]
    services: List[str]
    tags: Optional[str] = None
    resources: Optional[List[str]] = None
    confirm: bool = False

class ResourceResponse(BaseModel):
    id: str
    type: str
    region: str
    service: str
    name: Optional[str] = None
    tags: Dict[str, str] = {}
    created_time: Optional[str] = None
    state: Optional[str] = None

class DryRunResponse(BaseModel):
    total_resources: int
    resources_by_service: Dict[str, int]
    resources_by_region: Dict[str, int]
    resources: List[ResourceResponse]
    dependencies: List[Dict[str, Any]]

class DeleteResponse(BaseModel):
    status: str
    deleted_count: int
    failed_count: int
    results: List[Dict[str, Any]]

class ServiceInfo(BaseModel):
    name: str
    display_name: str
    category: str
    resource_types: List[str]

# In-memory storage for job tracking (replace with database in production)
job_store: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "AWS Nuker API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/services")
async def list_services() -> List[ServiceInfo]:
    """List all available AWS services supported by the nuker"""
    services_map = get_all_services()
    
    # Categorize services
    categories = {
        "Compute & Containers": ["ec2-instances", "ec2-volumes", "ec2-snapshots", "ec2-amis", 
                                  "ec2-elastic-ips", "ec2-key-pairs", "lambda", "batch-jobs", 
                                  "batch-compute-envs", "elastic-beanstalk", "app-runner", 
                                  "lightsail", "ecs-clusters", "eks-clusters", "ecr-repositories"],
        "Networking": ["vpcs", "subnets", "security-groups", "elb", "alb", "nlb"],
        "Storage": ["s3", "efs", "fsx", "storage-gateway", "glacier-vaults"],
        "Databases": ["rds-instances", "rds-clusters", "rds-snapshots", "dynamodb", 
                      "elasticache", "redshift"],
        "Analytics": ["athena", "emr", "glue-databases", "glue-crawlers", "opensearch", 
                     "data-pipeline"],
        "Application": ["api-gateway", "sns", "sqs", "kinesis"],
        "Management": ["cloudformation", "cloudwatch-alarms", "cloudwatch-logs", "route53", 
                      "backup"],
        "Developer Tools": ["codecommit", "codebuild", "codedeploy", "codepipeline", 
                           "codeartifact", "cloud9"],
        "Machine Learning": ["sagemaker-notebooks", "sagemaker-endpoints", "sagemaker-models", 
                            "comprehend", "rekognition"],
        "Security": ["iam-users", "iam-roles", "iam-policies", "iam-groups", "secrets-manager"]
    }
    
    result = []
    for category, service_list in categories.items():
        for service_name in service_list:
            result.append(ServiceInfo(
                name=service_name,
                display_name=service_name.replace("-", " ").title(),
                category=category,
                resource_types=[service_name]
            ))
    
    return result

@app.get("/api/regions")
async def list_regions() -> List[str]:
    """List all available AWS regions"""
    ec2 = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2.describe_regions()
        regions = [region['RegionName'] for region in response['Regions']]
        return sorted(regions)
    except Exception as e:
        logger.error(f"Failed to list regions: {e}")
        return ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", 
                "eu-central-1", "ap-southeast-1", "ap-northeast-1"]

@app.post("/api/discover")
async def discover_resources(request: DiscoverRequest) -> DryRunResponse:
    """Discover AWS resources based on filters"""
    try:
        services_map = get_all_services()
        all_resources = []
        resources_by_service = {}
        resources_by_region = {}
        
        # Parse tag filters if provided
        tag_filters = parse_tag_filters(request.tags) if request.tags else None
        
        # Process each region and service
        for region in request.regions:
            for service_name in request.services:
                if service_name not in services_map:
                    continue
                
                service_class = services_map[service_name]
                service = service_class(region=region, dry_run=True, tag_filters=tag_filters)
                
                try:
                    resources = service.list_resources()
                    
                    for resource in resources:
                        resource_data = ResourceResponse(
                            id=resource.get('id', resource.get('ResourceId', 'unknown')),
                            type=service_name,
                            region=region,
                            service=service_name.split('-')[0],
                            name=resource.get('name', resource.get('Name')),
                            tags=resource.get('tags', resource.get('Tags', {})),
                            created_time=resource.get('created_time', resource.get('CreateTime')),
                            state=resource.get('state', resource.get('State'))
                        )
                        all_resources.append(resource_data)
                        
                        # Count by service
                        resources_by_service[service_name] = resources_by_service.get(service_name, 0) + 1
                        # Count by region
                        resources_by_region[region] = resources_by_region.get(region, 0) + 1
                        
                except Exception as e:
                    logger.error(f"Error listing {service_name} in {region}: {e}")
                    continue
        
        return DryRunResponse(
            total_resources=len(all_resources),
            resources_by_service=resources_by_service,
            resources_by_region=resources_by_region,
            resources=all_resources,
            dependencies=[]
        )
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dryrun")
async def dry_run(request: DryRunRequest) -> DryRunResponse:
    """Simulate deletion without actually deleting resources"""
    return await discover_resources(DiscoverRequest(
        regions=request.regions,
        services=request.services,
        tags=request.tags
    ))

@app.post("/api/delete")
async def delete_resources(request: DeleteRequest, background_tasks: BackgroundTasks) -> DeleteResponse:
    """Execute resource deletion"""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Deletion must be confirmed")
    
    try:
        services_map = get_all_services()
        results = []
        deleted_count = 0
        failed_count = 0
        
        # Parse tag filters if provided
        tag_filters = parse_tag_filters(request.tags) if request.tags else None
        
        # Process each region and service
        for region in request.regions:
            for service_name in request.services:
                if service_name not in services_map:
                    continue
                
                service_class = services_map[service_name]
                service = service_class(region=region, dry_run=False, tag_filters=tag_filters)
                
                try:
                    # List and delete resources
                    service.cleanup()
                    results.append({
                        "service": service_name,
                        "region": region,
                        "status": "completed"
                    })
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting {service_name} in {region}: {e}")
                    results.append({
                        "service": service_name,
                        "region": region,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_count += 1
        
        return DeleteResponse(
            status="completed",
            deleted_count=deleted_count,
            failed_count=failed_count,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def get_reports() -> List[Dict[str, Any]]:
    """Get audit logs and cleanup reports"""
    # In production, this would query from database
    return []

@app.post("/api/estimate-cost")
async def estimate_cost(request: DiscoverRequest) -> Dict[str, Any]:
    """
    Estimate cost savings from deleting resources.
    
    Args:
        request: DiscoverRequest with regions, services, and optional tags
    
    Returns:
        Cost estimation including monthly/yearly savings and breakdown
    """
    try:
        services_map = get_all_services()
        all_resources = []
        
        # Parse tag filters if provided
        tag_filters = parse_tag_filters(request.tags) if request.tags else None
        
        # Discover resources
        for region in request.regions:
            cost_estimator = CostEstimator(region=region)
            
            for service_name in request.services:
                if service_name not in services_map:
                    continue
                
                service_class = services_map[service_name]
                service = service_class(region=region, dry_run=True, tag_filters=tag_filters)
                
                try:
                    resources = service.list_resources()
                    
                    # Add metadata for cost estimation
                    for resource in resources:
                        resource['service'] = service_name
                        resource['region'] = region
                        all_resources.append(resource)
                        
                except Exception as e:
                    logger.error(f"Error listing {service_name} in {region}: {e}")
                    continue
        
        if not all_resources:
            return {
                "resource_count": 0,
                "monthly_savings": 0,
                "yearly_savings": 0,
                "breakdown_by_service": {},
                "message": "No resources found matching criteria"
            }
        
        # Estimate cost savings
        cost_savings = cost_estimator.estimate_deletion_savings(all_resources)
        
        return {
            "resource_count": cost_savings['resource_count'],
            "monthly_savings": cost_savings['monthly_savings'],
            "yearly_savings": cost_savings['yearly_savings'],
            "breakdown_by_service": cost_savings['breakdown_by_service'],
            "note": "Cost estimates are approximate based on standard AWS pricing"
        }
        
    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
