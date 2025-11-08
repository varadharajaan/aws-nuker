"""
Base class for AWS resource handlers.

Provides common functionality for listing and deleting AWS resources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import boto3
from botocore.exceptions import ClientError

from .logger import get_logger


class ResourceHandler(ABC):
    """Abstract base class for AWS resource handlers."""

    def __init__(self, region: str, dry_run: bool = False, force: bool = False):
        """
        Initialize resource handler.

        Args:
            region: AWS region name
            dry_run: If True, only simulate deletions
            force: If True, force delete resources with dependencies
        """
        self.region = region
        self.dry_run = dry_run
        self.force = force
        self.logger = get_logger()
        self.session = boto3.Session(region_name=region)

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the AWS service name."""
        pass

    @abstractmethod
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all resources of this type in the region.

        Returns:
            List of resource dictionaries with at least 'id' and 'name' keys
        """
        pass

    @abstractmethod
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Delete a specific resource.

        Args:
            resource: Resource dictionary from list_resources()

        Returns:
            True if deletion succeeded, False otherwise
        """
        pass

    def is_default_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Check if resource is a default AWS resource that should be preserved.

        Args:
            resource: Resource dictionary

        Returns:
            True if resource is a default resource, False otherwise
        """
        # Override in subclasses for service-specific logic
        return False

    def nuke_all(self) -> Dict[str, Any]:
        """
        Delete all resources of this type in the region.

        Returns:
            Dictionary with deletion statistics
        """
        start_time = time.time()
        
        stats = {
            "service": self.service_name,
            "region": self.region,
            "total": 0,
            "deleted": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

        self.logger.info(
            f"Starting cleanup of {self.service_name} in {self.region}"
        )

        try:
            resources = self.list_resources()
            stats["total"] = len(resources)

            self.logger.info(
                f"Found {len(resources)} {self.service_name} resource(s)"
            )

            for resource in resources:
                resource_id = resource.get("id", "unknown")
                
                # Skip default resources unless forced
                if self.is_default_resource(resource) and not self.force:
                    self.logger.debug(
                        f"Skipping default resource: {resource_id}"
                    )
                    stats["skipped"] += 1
                    self.logger.audit(
                        action="DELETE",
                        resource_type=self.service_name,
                        resource_id=resource_id,
                        region=self.region,
                        status="SKIPPED",
                        details="Default resource",
                    )
                    continue

                # Perform deletion
                if self.dry_run:
                    self.logger.info(
                        f"[DRY RUN] Would delete {self.service_name}: {resource_id}"
                    )
                    stats["deleted"] += 1
                    self.logger.audit(
                        action="DELETE",
                        resource_type=self.service_name,
                        resource_id=resource_id,
                        region=self.region,
                        status="DRY_RUN",
                    )
                else:
                    success = self._delete_with_retry(resource)
                    if success:
                        stats["deleted"] += 1
                        self.logger.info(
                            f"Deleted {self.service_name}: {resource_id}"
                        )
                        self.logger.audit(
                            action="DELETE",
                            resource_type=self.service_name,
                            resource_id=resource_id,
                            region=self.region,
                            status="SUCCESS",
                        )
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(resource_id)

        except Exception as e:
            error_msg = f"Error during {self.service_name} cleanup: {str(e)}"
            self.logger.error(error_msg)
            stats["errors"].append(error_msg)

        elapsed_time = time.time() - start_time
        stats["elapsed_time"] = elapsed_time

        self.logger.info(
            f"Completed {self.service_name} cleanup in {elapsed_time:.2f}s - "
            f"Deleted: {stats['deleted']}, Failed: {stats['failed']}, "
            f"Skipped: {stats['skipped']}"
        )

        return stats

    def _delete_with_retry(
        self, resource: Dict[str, Any], max_retries: int = 3
    ) -> bool:
        """
        Delete resource with retry logic.

        Args:
            resource: Resource to delete
            max_retries: Maximum number of retry attempts

        Returns:
            True if deletion succeeded, False otherwise
        """
        resource_id = resource.get("id", "unknown")
        
        for attempt in range(max_retries):
            try:
                success = self.delete_resource(resource)
                if success:
                    return True
                
                # If delete_resource returns False, log and continue
                if attempt < max_retries - 1:
                    self.logger.debug(
                        f"Retry {attempt + 1}/{max_retries} for {resource_id}"
                    )
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                
                # Handle dependency violations with retry if force is enabled
                if error_code in ["DependencyViolation", "ResourceInUseException"]:
                    if self.force and attempt < max_retries - 1:
                        self.logger.warning(
                            f"Dependency violation for {resource_id}, retrying..."
                        )
                        time.sleep(5)  # Wait longer for dependencies
                        continue
                    else:
                        self.logger.error(
                            f"Cannot delete {resource_id}: {error_code}"
                        )
                        self.logger.audit(
                            action="DELETE",
                            resource_type=self.service_name,
                            resource_id=resource_id,
                            region=self.region,
                            status="FAILED",
                            details=f"Dependency violation: {error_code}",
                        )
                        return False
                else:
                    self.logger.error(
                        f"Error deleting {resource_id}: {str(e)}"
                    )
                    self.logger.audit(
                        action="DELETE",
                        resource_type=self.service_name,
                        resource_id=resource_id,
                        region=self.region,
                        status="FAILED",
                        details=str(e),
                    )
                    return False
                    
            except Exception as e:
                self.logger.error(
                    f"Unexpected error deleting {resource_id}: {str(e)}"
                )
                self.logger.audit(
                    action="DELETE",
                    resource_type=self.service_name,
                    resource_id=resource_id,
                    region=self.region,
                    status="FAILED",
                    details=str(e),
                )
                return False

        # All retries exhausted
        self.logger.error(
            f"Failed to delete {resource_id} after {max_retries} attempts"
        )
        self.logger.audit(
            action="DELETE",
            resource_type=self.service_name,
            resource_id=resource_id,
            region=self.region,
            status="FAILED",
            details="Max retries exhausted",
        )
        return False
