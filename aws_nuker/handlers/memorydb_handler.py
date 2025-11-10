"""Handler for MEMORYDB resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MemorydbHandler(ResourceHandler):
    """Handler for MEMORYDB resources."""

    @property
    def service_name(self) -> str:
        return "memorydb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEMORYDB resources."""
        client = self.session.client("memorydb")
        resources = []

        try:
            paginator = client.get_paginator("describe_clusters")
            for page in paginator.paginate():
                for item in page.get("Clusters", []):
                    resources.append({
                        "id": item.get("Name", ""),
                        "name": item.get("Name", ""),
                        "type": "cluster",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing MEMORYDB resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEMORYDB resource."""
        client = self.session.client("memorydb")
        resource_id = resource.get("id")

        try:
            client.delete_cluster(ClusterName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEMORYDB resource {resource_id}: {str(e)}")
            return False
