"""Handler for CLOUDHSM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudhsmHandler(ResourceHandler):
    """Handler for CLOUDHSM resources."""

    @property
    def service_name(self) -> str:
        return "cloudhsm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUDHSM resources."""
        client = self.session.client("cloudhsmv2")
        resources = []

        try:
            paginator = client.get_paginator("describe_clusters")
            for page in paginator.paginate():
                for item in page.get("Clusters", []):
                    resources.append({
                        "id": item.get("ClusterId", ""),
                        "name": item.get("ClusterId", ""),
                        "type": "cluster",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUDHSM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUDHSM resource."""
        client = self.session.client("cloudhsmv2")
        resource_id = resource.get("id")

        try:
            client.delete_cluster(ClusterId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUDHSM resource {resource_id}: {str(e)}")
            return False
