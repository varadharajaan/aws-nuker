"""
Base Service Class for AWS Resource Cleanup
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style


class BaseService(ABC):
    """
    Base class for all AWS service cleanup implementations
    """
    
    def __init__(self, region: str, dry_run: bool = False, tag_filters: List[str] = None):
        """
        Initialize the service
        
        Args:
            region: AWS region name
            dry_run: If True, only show what would be deleted without deleting
            tag_filters: List of tag filter strings (e.g., ['env=dev', 'owner=*'])
        """
        self.region = region
        self.dry_run = dry_run
        self.tag_filters = tag_filters or []
        self.deleted_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
    @abstractmethod
    def get_service_name(self) -> str:
        """Return the service name"""
        pass
    
    @abstractmethod
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all resources for this service in the region
        
        Returns:
            List of resource dictionaries with at least 'id' and 'name' keys
        """
        pass
    
    @abstractmethod
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Delete a single resource
        
        Args:
            resource: Resource dictionary
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    def cleanup(self) -> Dict[str, int]:
        """
        Main cleanup method that lists and deletes all resources
        
        Note: This method logs AWS resource identifiers (instance IDs, bucket names, etc.)
        which are necessary for tracking and transparency. These are not secrets.
        
        Returns:
            Dictionary with counts of deleted, failed, and skipped resources
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Cleaning up {self.get_service_name()} in {self.region}{Style.RESET_ALL}")
        if self.tag_filters:
            print(f"{Fore.CYAN}Tag filters: {', '.join(self.tag_filters)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        try:
            resources = self.list_resources()
            
            if not resources:
                print(f"{Fore.YELLOW}No resources found for {self.get_service_name()}{Style.RESET_ALL}")
                return {'deleted': 0, 'failed': 0, 'skipped': 0}
            
            # Filter resources by tags if filters are provided
            if self.tag_filters:
                filtered_resources = self.filter_resources_by_tags(resources)
                print(f"Found {len(resources)} resources, {len(filtered_resources)} match tag filters\n")
                resources = filtered_resources
            else:
                print(f"Found {len(resources)} resources\n")
            
            if not resources:
                print(f"{Fore.YELLOW}No resources match the tag filters{Style.RESET_ALL}")
                return {'deleted': 0, 'failed': 0, 'skipped': 0}
            
            for resource in resources:
                resource_id = resource.get('id', 'unknown')
                resource_name = resource.get('name', 'N/A')
                
                if self.dry_run:
                    # lgtm[py/clear-text-logging-sensitive-data]
                    # Resource IDs and names are not secrets - they're AWS identifiers needed for transparency
                    print(f"{Fore.YELLOW}[DRY RUN] Would delete: {resource_id} ({resource_name}){Style.RESET_ALL}")
                    self.deleted_count += 1
                else:
                    try:
                        if self.delete_resource(resource):
                            # lgtm[py/clear-text-logging-sensitive-data]
                            # Resource IDs and names are not secrets - they're AWS identifiers needed for transparency
                            print(f"{Fore.GREEN}✓ Deleted: {resource_id} ({resource_name}){Style.RESET_ALL}")
                            self.deleted_count += 1
                        else:
                            # lgtm[py/clear-text-logging-sensitive-data]
                            # Resource IDs and names are not secrets - they're AWS identifiers needed for transparency
                            print(f"{Fore.YELLOW}⊘ Skipped: {resource_id} ({resource_name}){Style.RESET_ALL}")
                            self.skipped_count += 1
                    except Exception as e:
                        # lgtm[py/clear-text-logging-sensitive-data]
                        # Resource IDs are not secrets - they're AWS identifiers needed for debugging
                        print(f"{Fore.RED}✗ Failed to delete {resource_id}: {str(e)}{Style.RESET_ALL}")
                        self.failed_count += 1
            
            print(f"\n{Fore.CYAN}Summary for {self.get_service_name()}:{Style.RESET_ALL}")
            print(f"  Deleted: {self.deleted_count}")
            print(f"  Failed: {self.failed_count}")
            print(f"  Skipped: {self.skipped_count}")
            
        except Exception as e:
            print(f"{Fore.RED}Error cleaning up {self.get_service_name()}: {str(e)}{Style.RESET_ALL}")
        
        return {
            'deleted': self.deleted_count,
            'failed': self.failed_count,
            'skipped': self.skipped_count
        }
    
    def filter_resources_by_tags(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter resources based on tag filters
        
        Args:
            resources: List of resources
            
        Returns:
            Filtered list of resources that match tag criteria
        """
        if not self.tag_filters:
            return resources
        
        from ..utils import matches_tag_filters
        
        filtered = []
        for resource in resources:
            # Get tags from resource (different services may store tags differently)
            tags = resource.get('tags', resource.get('Tags', []))
            
            if matches_tag_filters(tags, self.tag_filters):
                filtered.append(resource)
        
        return filtered
    
    def log_error(self, message: str, error: Exception = None):
        """
        Log an error message
        
        Note: This logs AWS resource identifiers (IDs, names) which are not secrets.
        These are necessary for users to track which resources are being processed.
        """
        error_msg = f"{message}"
        if error:
            # Don't log full exception details that might contain sensitive info
            error_msg += f": {type(error).__name__}"
        # lgtm[py/clear-text-logging-sensitive-data]
        # Error messages contain resource identifiers, not secrets
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
