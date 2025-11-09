"""
Cost estimation module for AWS resources.

Provides cost analysis before deletion using AWS pricing data and resource metadata.
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CostEstimator:
    """Estimates costs for AWS resources before deletion."""
    
    # Approximate hourly costs (USD) - simplified for estimation
    # In production, should query AWS Price List API
    HOURLY_COSTS = {
        'ec2': {
            't2.micro': 0.0116,
            't2.small': 0.023,
            't2.medium': 0.0464,
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'default': 0.05  # fallback
        },
        'rds': {
            'db.t2.micro': 0.017,
            'db.t2.small': 0.034,
            'db.t3.micro': 0.017,
            'db.t3.small': 0.034,
            'db.m5.large': 0.18,
            'default': 0.10
        }
    }
    
    # Storage costs per GB-month (USD)
    STORAGE_COSTS = {
        's3': 0.023,  # Standard
        's3-ia': 0.0125,  # Infrequent Access
        's3-glacier': 0.004,
        'ebs-gp2': 0.10,
        'ebs-gp3': 0.08,
        'ebs-io1': 0.125,
        'ebs-st1': 0.045,
        'ebs-sc1': 0.025,
        'snapshot': 0.05,
        'efs': 0.30,
        'fsx': 0.14
    }
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize cost estimator.
        
        Args:
            region: AWS region for pricing
        """
        self.region = region
        self.pricing_client = None
        try:
            # Pricing API is only available in us-east-1
            self.pricing_client = boto3.client('pricing', region_name='us-east-1')
        except Exception as e:
            logger.warning(f"Could not initialize pricing client: {e}")
    
    def estimate_ec2_cost(self, instance_type: str, uptime_hours: Optional[int] = None) -> Dict:
        """
        Estimate EC2 instance cost.
        
        Args:
            instance_type: EC2 instance type (e.g., 't2.micro')
            uptime_hours: Hours instance has been running (for total cost)
        
        Returns:
            Dict with cost estimates
        """
        hourly_cost = self.HOURLY_COSTS['ec2'].get(
            instance_type,
            self.HOURLY_COSTS['ec2']['default']
        )
        
        monthly_cost = hourly_cost * 730  # Average hours per month
        
        result = {
            'hourly_cost': round(hourly_cost, 4),
            'daily_cost': round(hourly_cost * 24, 2),
            'monthly_cost': round(monthly_cost, 2),
            'yearly_cost': round(monthly_cost * 12, 2)
        }
        
        if uptime_hours:
            result['total_cost_to_date'] = round(hourly_cost * uptime_hours, 2)
        
        return result
    
    def estimate_storage_cost(self, storage_type: str, size_gb: float, 
                             days_stored: Optional[int] = None) -> Dict:
        """
        Estimate storage cost.
        
        Args:
            storage_type: Type of storage (e.g., 's3', 'ebs-gp2')
            size_gb: Size in GB
            days_stored: Number of days stored (for total cost)
        
        Returns:
            Dict with cost estimates
        """
        monthly_cost_per_gb = self.STORAGE_COSTS.get(storage_type, 0.10)
        monthly_cost = size_gb * monthly_cost_per_gb
        
        result = {
            'size_gb': round(size_gb, 2),
            'monthly_cost_per_gb': monthly_cost_per_gb,
            'monthly_cost': round(monthly_cost, 2),
            'yearly_cost': round(monthly_cost * 12, 2)
        }
        
        if days_stored:
            daily_cost = monthly_cost / 30
            result['total_cost_to_date'] = round(daily_cost * days_stored, 2)
        
        return result
    
    def estimate_rds_cost(self, instance_class: str, storage_gb: float,
                         uptime_hours: Optional[int] = None) -> Dict:
        """
        Estimate RDS instance cost.
        
        Args:
            instance_class: RDS instance class (e.g., 'db.t2.micro')
            storage_gb: Storage size in GB
            uptime_hours: Hours instance has been running
        
        Returns:
            Dict with cost estimates
        """
        hourly_cost = self.HOURLY_COSTS['rds'].get(
            instance_class,
            self.HOURLY_COSTS['rds']['default']
        )
        
        # RDS storage cost (GP2)
        storage_monthly = storage_gb * 0.115  # $0.115 per GB-month for GP2
        
        instance_monthly = hourly_cost * 730
        total_monthly = instance_monthly + storage_monthly
        
        result = {
            'instance_hourly_cost': round(hourly_cost, 4),
            'instance_monthly_cost': round(instance_monthly, 2),
            'storage_monthly_cost': round(storage_monthly, 2),
            'total_monthly_cost': round(total_monthly, 2),
            'total_yearly_cost': round(total_monthly * 12, 2)
        }
        
        if uptime_hours:
            instance_cost = hourly_cost * uptime_hours
            storage_days = uptime_hours / 24
            storage_cost = (storage_monthly / 30) * storage_days
            result['total_cost_to_date'] = round(instance_cost + storage_cost, 2)
        
        return result
    
    def estimate_lambda_cost(self, invocations: int, avg_duration_ms: int,
                            memory_mb: int) -> Dict:
        """
        Estimate Lambda function cost.
        
        Args:
            invocations: Number of monthly invocations
            avg_duration_ms: Average duration in milliseconds
            memory_mb: Memory allocation in MB
        
        Returns:
            Dict with cost estimates
        """
        # Lambda pricing
        request_cost = invocations * 0.0000002  # $0.20 per 1M requests
        
        # Compute cost: $0.0000166667 per GB-second
        gb_seconds = (memory_mb / 1024) * (avg_duration_ms / 1000) * invocations
        compute_cost = gb_seconds * 0.0000166667
        
        total_monthly = request_cost + compute_cost
        
        return {
            'invocations': invocations,
            'request_cost': round(request_cost, 4),
            'compute_cost': round(compute_cost, 4),
            'total_monthly_cost': round(total_monthly, 4),
            'total_yearly_cost': round(total_monthly * 12, 2)
        }
    
    def estimate_s3_cost(self, bucket_size_gb: float, requests_per_month: int = 0) -> Dict:
        """
        Estimate S3 bucket cost.
        
        Args:
            bucket_size_gb: Total bucket size in GB
            requests_per_month: Number of requests per month
        
        Returns:
            Dict with cost estimates
        """
        # Standard storage cost
        storage_cost = bucket_size_gb * self.STORAGE_COSTS['s3']
        
        # Request costs (simplified)
        # PUT/COPY/POST/LIST: $0.005 per 1,000 requests
        # GET/SELECT: $0.0004 per 1,000 requests
        request_cost = (requests_per_month / 1000) * 0.005
        
        total_monthly = storage_cost + request_cost
        
        return {
            'size_gb': round(bucket_size_gb, 2),
            'storage_monthly_cost': round(storage_cost, 2),
            'request_monthly_cost': round(request_cost, 4),
            'total_monthly_cost': round(total_monthly, 2),
            'total_yearly_cost': round(total_monthly * 12, 2)
        }
    
    def estimate_deletion_savings(self, resources: List[Dict]) -> Dict:
        """
        Estimate total cost savings from deleting resources.
        
        Args:
            resources: List of resource dicts with type and metadata
        
        Returns:
            Dict with aggregated cost savings
        """
        total_monthly = 0
        breakdown = {}
        
        for resource in resources:
            service = resource.get('service', 'unknown')
            
            if service == 'ec2-instances':
                instance_type = resource.get('instance_type', 't2.micro')
                cost = self.estimate_ec2_cost(instance_type)
                monthly = cost['monthly_cost']
            
            elif service == 's3-buckets':
                size_gb = resource.get('size_gb', 0)
                cost = self.estimate_s3_cost(size_gb)
                monthly = cost['total_monthly_cost']
            
            elif service == 'ebs-volumes':
                size_gb = resource.get('size_gb', 0)
                vol_type = resource.get('volume_type', 'gp2')
                storage_key = f'ebs-{vol_type}'
                cost = self.estimate_storage_cost(storage_key, size_gb)
                monthly = cost['monthly_cost']
            
            elif service == 'rds-instances':
                instance_class = resource.get('instance_class', 'db.t2.micro')
                storage_gb = resource.get('storage_gb', 20)
                cost = self.estimate_rds_cost(instance_class, storage_gb)
                monthly = cost['total_monthly_cost']
            
            else:
                # Default estimate for unknown services
                monthly = 10.0  # Placeholder
            
            total_monthly += monthly
            breakdown[service] = breakdown.get(service, 0) + monthly
        
        return {
            'resource_count': len(resources),
            'monthly_savings': round(total_monthly, 2),
            'yearly_savings': round(total_monthly * 12, 2),
            'breakdown_by_service': {k: round(v, 2) for k, v in breakdown.items()}
        }
    
    def get_resource_age_days(self, created_time: datetime) -> int:
        """
        Calculate resource age in days.
        
        Args:
            created_time: Resource creation timestamp
        
        Returns:
            Age in days
        """
        now = datetime.now(created_time.tzinfo) if created_time.tzinfo else datetime.now()
        age = now - created_time
        return age.days
    
    def format_cost_report(self, cost_data: Dict) -> str:
        """
        Format cost data into a readable report.
        
        Args:
            cost_data: Cost estimation dict
        
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("COST ESTIMATION REPORT")
        lines.append("=" * 60)
        
        if 'resource_count' in cost_data:
            lines.append(f"\nResources to delete: {cost_data['resource_count']}")
            lines.append(f"\nEstimated Monthly Savings: ${cost_data['monthly_savings']:.2f}")
            lines.append(f"Estimated Yearly Savings: ${cost_data['yearly_savings']:.2f}")
            
            if 'breakdown_by_service' in cost_data:
                lines.append("\nSavings Breakdown by Service:")
                for service, cost in cost_data['breakdown_by_service'].items():
                    lines.append(f"  - {service}: ${cost:.2f}/month")
        else:
            for key, value in cost_data.items():
                if isinstance(value, (int, float)):
                    lines.append(f"{key}: ${value:.2f}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
