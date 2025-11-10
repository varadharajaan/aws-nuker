"""Handler for BATCH resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class BatchHandler(ResourceHandler):
    """Handler for BATCH resources."""

    @property
    def service_name(self) -> str:
        return "batch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all BATCH resources."""
        client = self.session.client("batch")
        resources = []

        try:
            paginator = client.get_paginator("describe_compute_environments")
            for page in paginator.paginate():
                for item in page.get("computeEnvironments", []):
                    resources.append({
                        "id": item.get("computeEnvironmentArn", ""),
                        "name": item.get("computeEnvironmentName", ""),
                        "type": "environment",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing BATCH resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a BATCH resource."""
        client = self.session.client("batch")
        resource_id = resource.get("id")

        try:
            client.delete_compute_environment(computeEnvironment=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting BATCH resource {resource_id}: {str(e)}")
            return False
