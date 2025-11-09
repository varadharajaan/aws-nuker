"""
Tag-based resource discovery and management for AWS Nuker.

Provides intelligent tag grouping, pattern matching, and tag-based cleanup.
"""

import re
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import boto3
import logging

logger = logging.getLogger(__name__)


@dataclass
class TagFilter:
    """Represents a tag-based filter condition."""

    key: Optional[str] = None
    value: Optional[str] = None
    operator: str = "equals"  # equals, starts_with, contains, regex, exists, not_exists
    
    def matches(self, tags: Dict[str, str]) -> bool:
        """Check if tags match this filter."""
        if self.operator == "exists":
            return self.key in tags
        
        if self.operator == "not_exists":
            return self.key not in tags
        
        if self.key not in tags:
            return False
        
        tag_value = tags[self.key]
        
        if self.operator == "equals":
            return tag_value == self.value
        
        if self.operator == "starts_with":
            return tag_value.startswith(self.value)
        
        if self.operator == "contains":
            return self.value in tag_value
        
        if self.operator == "regex":
            try:
                return bool(re.match(self.value, tag_value))
            except re.error:
                logger.warning(f"Invalid regex pattern: {self.value}")
                return False
        
        return False


@dataclass
class TagGroup:
    """Represents a group of resources with similar tags."""

    tag_hash: str
    tags: Dict[str, str]
    resources: List[Dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    oldest_age_days: int = 0
    
    @property
    def resource_count(self) -> int:
        """Get number of resources in this group."""
        return len(self.resources)
    
    @property
    def resource_types(self) -> Set[str]:
        """Get unique resource types in this group."""
        return {r.get('ResourceType', 'Unknown') for r in self.resources}


@dataclass
class TagDiscoveryResult:
    """Results from tag discovery operation."""

    total_resources: int = 0
    tagged_resources: int = 0
    untagged_resources: int = 0
    tag_groups: List[TagGroup] = field(default_factory=list)
    resources_by_tag: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


class TagManager:
    """Manages tag-based resource discovery and filtering."""

    def __init__(self, region: str = "us-east-1"):
        """
        Initialize TagManager.

        Args:
            region: AWS region to operate in
        """
        self.region = region
        self.resource_groups_client = boto3.client('resourcegroupstaggingapi', region_name=region)
    
    def discover_resources(
        self,
        resource_types: Optional[List[str]] = None,
        tag_filters: Optional[List[TagFilter]] = None
    ) -> TagDiscoveryResult:
        """
        Discover AWS resources and their tags.

        Args:
            resource_types: Filter by resource types (e.g., ['ec2:instance', 's3:bucket'])
            tag_filters: List of tag filters to apply

        Returns:
            TagDiscoveryResult with discovered resources grouped by tags
        """
        logger.info(f"Starting tag discovery in region {self.region}")
        
        result = TagDiscoveryResult()
        all_resources = []
        
        try:
            # Use Resource Groups Tagging API for comprehensive discovery
            paginator = self.resource_groups_client.get_paginator('get_resources')
            
            page_params = {}
            if resource_types:
                page_params['ResourceTypeFilters'] = resource_types
            
            for page in paginator.paginate(**page_params):
                all_resources.extend(page.get('ResourceTagMappingList', []))
            
            result.total_resources = len(all_resources)
            
            # Group resources by tags
            tag_groups_dict = defaultdict(list)
            
            for resource in all_resources:
                arn = resource.get('ResourceARN', '')
                tags_list = resource.get('Tags', [])
                
                # Convert tag list to dictionary
                tags_dict = {tag['Key']: tag['Value'] for tag in tags_list}
                
                resource_info = {
                    'ARN': arn,
                    'Tags': tags_dict,
                    'ResourceType': self._extract_resource_type(arn)
                }
                
                # Check if resource has tags
                if tags_dict:
                    result.tagged_resources += 1
                    
                    # Apply tag filters if specified
                    if tag_filters:
                        if self._matches_filters(tags_dict, tag_filters):
                            # Create tag hash for grouping
                            tag_hash = self._create_tag_hash(tags_dict)
                            tag_groups_dict[tag_hash].append(resource_info)
                    else:
                        tag_hash = self._create_tag_hash(tags_dict)
                        tag_groups_dict[tag_hash].append(resource_info)
                else:
                    result.untagged_resources += 1
                    # Group untagged resources separately
                    tag_groups_dict['UNTAGGED'].append(resource_info)
            
            # Create TagGroup objects
            for tag_hash, resources in tag_groups_dict.items():
                if tag_hash == 'UNTAGGED':
                    tags = {}
                else:
                    tags = resources[0]['Tags'] if resources else {}
                
                tag_group = TagGroup(
                    tag_hash=tag_hash,
                    tags=tags,
                    resources=resources
                )
                result.tag_groups.append(tag_group)
            
            # Sort tag groups by resource count (descending)
            result.tag_groups.sort(key=lambda g: g.resource_count, reverse=True)
            
            logger.info(f"Discovery complete: {result.total_resources} total, "
                       f"{result.tagged_resources} tagged, "
                       f"{result.untagged_resources} untagged, "
                       f"{len(result.tag_groups)} tag groups")
            
        except Exception as e:
            logger.error(f"Error during tag discovery: {e}")
        
        return result
    
    def filter_by_tag_pattern(
        self,
        key_pattern: Optional[str] = None,
        value_pattern: Optional[str] = None,
        use_regex: bool = False
    ) -> List[TagFilter]:
        """
        Create tag filters from patterns.

        Args:
            key_pattern: Pattern to match tag keys
            value_pattern: Pattern to match tag values
            use_regex: Whether to use regex matching

        Returns:
            List of TagFilter objects
        """
        filters = []
        
        if key_pattern:
            if use_regex:
                # Create regex filter
                filters.append(TagFilter(key=key_pattern, operator="regex"))
            elif "*" in key_pattern:
                # Convert wildcard to regex
                regex_pattern = key_pattern.replace("*", ".*")
                filters.append(TagFilter(key=regex_pattern, operator="regex"))
            else:
                filters.append(TagFilter(key=key_pattern, operator="equals"))
        
        if value_pattern:
            if use_regex:
                filters.append(TagFilter(value=value_pattern, operator="regex"))
            elif "*" in value_pattern:
                regex_pattern = value_pattern.replace("*", ".*")
                filters.append(TagFilter(value=regex_pattern, operator="regex"))
        
        return filters
    
    def filter_untagged_resources(self, discovery_result: TagDiscoveryResult) -> List[Dict[str, Any]]:
        """
        Extract untagged resources from discovery result.

        Args:
            discovery_result: Result from discover_resources

        Returns:
            List of untagged resources
        """
        untagged = []
        for tag_group in discovery_result.tag_groups:
            if tag_group.tag_hash == 'UNTAGGED':
                untagged.extend(tag_group.resources)
        
        return untagged
    
    def get_resources_by_tags(
        self,
        tag_conditions: Dict[str, str],
        match_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get resources matching specific tag conditions.

        Args:
            tag_conditions: Dictionary of tag key-value pairs
            match_all: If True, resource must match all conditions (AND logic)
                      If False, resource can match any condition (OR logic)

        Returns:
            List of matching resources
        """
        discovery_result = self.discover_resources()
        matching_resources = []
        
        for tag_group in discovery_result.tag_groups:
            for resource in tag_group.resources:
                resource_tags = resource.get('Tags', {})
                
                if match_all:
                    # AND logic - all conditions must match
                    if all(resource_tags.get(k) == v for k, v in tag_conditions.items()):
                        matching_resources.append(resource)
                else:
                    # OR logic - any condition can match
                    if any(resource_tags.get(k) == v for k, v in tag_conditions.items()):
                        matching_resources.append(resource)
        
        return matching_resources
    
    def suggest_cleanup_targets(
        self,
        min_resource_count: int = 5,
        min_age_days: int = 90
    ) -> List[Tuple[TagGroup, str]]:
        """
        Suggest tag groups that might be good candidates for cleanup.

        Args:
            min_resource_count: Minimum number of resources to suggest
            min_age_days: Minimum age in days for resources

        Returns:
            List of (TagGroup, reason) tuples
        """
        discovery_result = self.discover_resources()
        suggestions = []
        
        for tag_group in discovery_result.tag_groups:
            reasons = []
            
            # Check for dev/test environments
            env_tag = tag_group.tags.get('env', '').lower()
            environment_tag = tag_group.tags.get('environment', '').lower()
            
            if env_tag in ['dev', 'development', 'test', 'testing', 'staging']:
                reasons.append(f"Dev/test environment (env={env_tag})")
            elif environment_tag in ['dev', 'development', 'test', 'testing', 'staging']:
                reasons.append(f"Dev/test environment (environment={environment_tag})")
            
            # Check for large resource groups
            if tag_group.resource_count >= min_resource_count:
                reasons.append(f"{tag_group.resource_count} resources in group")
            
            # Check for temporary tags
            for key in tag_group.tags:
                if 'temp' in key.lower() or 'temporary' in key.lower():
                    reasons.append(f"Temporary tag: {key}")
            
            if reasons:
                suggestion_reason = "; ".join(reasons)
                suggestions.append((tag_group, suggestion_reason))
        
        return suggestions
    
    def _extract_resource_type(self, arn: str) -> str:
        """Extract resource type from ARN."""
        try:
            parts = arn.split(':')
            if len(parts) >= 6:
                service = parts[2]
                resource_part = parts[5]
                
                # Handle different ARN formats
                if '/' in resource_part:
                    resource_type = resource_part.split('/')[0]
                else:
                    resource_type = resource_part.split(':')[0] if ':' in resource_part else resource_part
                
                return f"{service}:{resource_type}"
        except Exception:
            pass
        
        return "Unknown"
    
    def _create_tag_hash(self, tags: Dict[str, str]) -> str:
        """Create a hash from tags for grouping."""
        # Sort tags by key and create a stable hash
        sorted_items = sorted(tags.items())
        return str(hash(tuple(sorted_items)))
    
    def _matches_filters(self, tags: Dict[str, str], filters: List[TagFilter]) -> bool:
        """Check if tags match all filters (AND logic)."""
        return all(f.matches(tags) for f in filters)
