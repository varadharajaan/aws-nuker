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
    
    def __init__(self, region: str, dry_run: bool = False):
        """
        Initialize the service
        
        Args:
            region: AWS region name
            dry_run: If True, only show what would be deleted without deleting
        """
        self.region = region
        self.dry_run = dry_run
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
        
        Returns:
            Dictionary with counts of deleted, failed, and skipped resources
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Cleaning up {self.get_service_name()} in {self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        try:
            resources = self.list_resources()
            
            if not resources:
                print(f"{Fore.YELLOW}No resources found for {self.get_service_name()}{Style.RESET_ALL}")
                return {'deleted': 0, 'failed': 0, 'skipped': 0}
            
            print(f"Found {len(resources)} resources\n")
            
            for resource in resources:
                resource_id = resource.get('id', 'unknown')
                resource_name = resource.get('name', 'N/A')
                
                if self.dry_run:
                    print(f"{Fore.YELLOW}[DRY RUN] Would delete: {resource_id} ({resource_name}){Style.RESET_ALL}")
                    self.deleted_count += 1
                else:
                    try:
                        if self.delete_resource(resource):
                            print(f"{Fore.GREEN}✓ Deleted: {resource_id} ({resource_name}){Style.RESET_ALL}")
                            self.deleted_count += 1
                        else:
                            print(f"{Fore.YELLOW}⊘ Skipped: {resource_id} ({resource_name}){Style.RESET_ALL}")
                            self.skipped_count += 1
                    except Exception as e:
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
    
    def log_error(self, message: str, error: Exception = None):
        """Log an error message"""
        error_msg = f"{message}"
        if error:
            error_msg += f": {str(error)}"
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
