"""
Utility functions for AWS Nuker
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any
import re


def parse_regions(region_input: str) -> List[str]:
    """
    Parse region input which can be:
    - Single region: 'us-east-1'
    - Multiple regions: 'us-east-1,us-west-2'
    - All regions: 'all'
    
    Returns:
        List of region names
    """
    if not region_input or region_input.strip().lower() == 'all':
        # Get all available regions
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        try:
            regions = ec2_client.describe_regions()['Regions']
            return [region['RegionName'] for region in regions]
        except Exception as e:
            print(f"Error fetching regions: {e}")
            return []
    
    # Split by comma and strip whitespace
    regions = [r.strip() for r in region_input.split(',')]
    return regions


def get_default_vpc_id(ec2_client) -> str:
    """
    Get the default VPC ID for a region
    
    Args:
        ec2_client: boto3 EC2 client
        
    Returns:
        Default VPC ID or empty string if not found
    """
    try:
        vpcs = ec2_client.describe_vpcs(
            Filters=[{'Name': 'isDefault', 'Values': ['true']}]
        )
        if vpcs['Vpcs']:
            return vpcs['Vpcs'][0]['VpcId']
    except Exception:
        pass
    return ''


def is_default_resource(resource_type: str, resource_id: str, **kwargs) -> bool:
    """
    Check if a resource is a default AWS resource that should not be deleted
    
    Args:
        resource_type: Type of resource (vpc, subnet, sg, etc.)
        resource_id: Resource ID
        **kwargs: Additional context (vpc_id, is_default flag, etc.)
        
    Returns:
        True if resource is default and should be skipped
    """
    # Default VPCs
    if resource_type == 'vpc':
        return kwargs.get('is_default', False)
    
    # Resources in default VPC
    if resource_type in ['subnet', 'security_group', 'route_table', 'network_acl', 'internet_gateway']:
        default_vpc_id = kwargs.get('default_vpc_id', '')
        resource_vpc_id = kwargs.get('vpc_id', '')
        return default_vpc_id and resource_vpc_id == default_vpc_id
    
    # Default security group
    if resource_type == 'security_group':
        sg_name = kwargs.get('group_name', '')
        return sg_name == 'default'
    
    return False


def retry_with_backoff(func, max_retries=3, exceptions=(ClientError,)):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Function result or raises last exception
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    

def handle_dependencies(resource_type: str, resource_id: str, client, **kwargs):
    """
    Handle dependencies before deleting a resource
    This function forcefully deletes dependent resources
    
    Args:
        resource_type: Type of resource
        resource_id: Resource ID
        client: boto3 client
        **kwargs: Additional context
    """
    # This is a placeholder for dependency handling
    # Specific implementations will be in service classes
    pass
