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


def parse_tag_filter(tag_filter: str) -> Dict[str, Any]:
    """
    Parse tag filter string into structured format
    
    Supported formats:
    - key=value (exact match)
    - key=value* (prefix match)
    - key=*value (suffix match)
    - key=*value* (contains match)
    - key (tag exists)
    - !key (tag does not exist)
    
    Args:
        tag_filter: Tag filter string
        
    Returns:
        Dictionary with filter criteria
    """
    tag_filter = tag_filter.strip()
    
    # Check for negation (tag should NOT exist)
    if tag_filter.startswith('!'):
        return {
            'key': tag_filter[1:],
            'operator': 'not_exists'
        }
    
    # Check if contains '=' (key-value pair)
    if '=' in tag_filter:
        key, value = tag_filter.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Determine match type based on wildcards
        if value.startswith('*') and value.endswith('*'):
            # Contains match
            return {
                'key': key,
                'value': value.strip('*'),
                'operator': 'contains'
            }
        elif value.startswith('*'):
            # Suffix match
            return {
                'key': key,
                'value': value[1:],
                'operator': 'suffix'
            }
        elif value.endswith('*'):
            # Prefix match
            return {
                'key': key,
                'value': value[:-1],
                'operator': 'prefix'
            }
        else:
            # Exact match
            return {
                'key': key,
                'value': value,
                'operator': 'exact'
            }
    else:
        # Tag key exists (any value)
        return {
            'key': tag_filter,
            'operator': 'exists'
        }


def matches_tag_filter(tags: List[Dict[str, str]], filter_criteria: Dict[str, Any]) -> bool:
    """
    Check if resource tags match the filter criteria
    
    Args:
        tags: List of tag dictionaries with 'Key' and 'Value'
        filter_criteria: Parsed filter criteria from parse_tag_filter
        
    Returns:
        True if tags match the filter, False otherwise
    """
    key = filter_criteria['key']
    operator = filter_criteria['operator']
    
    # Find tag with matching key
    tag_value = None
    for tag in tags:
        if tag.get('Key') == key:
            tag_value = tag.get('Value', '')
            break
    
    # Apply operator
    if operator == 'exists':
        return tag_value is not None
    elif operator == 'not_exists':
        return tag_value is None
    elif operator == 'exact':
        return tag_value == filter_criteria['value']
    elif operator == 'prefix':
        return tag_value is not None and tag_value.startswith(filter_criteria['value'])
    elif operator == 'suffix':
        return tag_value is not None and tag_value.endswith(filter_criteria['value'])
    elif operator == 'contains':
        return tag_value is not None and filter_criteria['value'] in tag_value
    
    return False


def matches_tag_filters(tags: List[Dict[str, str]], filters: List[str]) -> bool:
    """
    Check if resource tags match ALL provided filters (AND logic)
    
    Args:
        tags: List of tag dictionaries with 'Key' and 'Value'
        filters: List of tag filter strings
        
    Returns:
        True if tags match all filters, False otherwise
    """
    if not filters:
        return True  # No filters means match everything
    
    for filter_str in filters:
        criteria = parse_tag_filter(filter_str)
        if not matches_tag_filter(tags, criteria):
            return False
    
    return True
