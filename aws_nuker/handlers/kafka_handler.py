"""Handler for KAFKA resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KafkaHandler(ResourceHandler):
    """Handler for KAFKA resources."""

    @property
    def service_name(self) -> str:
        return "kafka"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all KAFKA resources."""
        client = self.session.client("kafka")
        resources = []

        try:
            paginator = client.get_paginator("list_clusters")
            for page in paginator.paginate():
                for item in page.get("ClusterInfoList", []):
                    resources.append({
                        "id": item.get("ClusterArn", ""),
                        "name": item.get("ClusterName", ""),
                        "type": "cluster",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing KAFKA resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a KAFKA resource."""
        client = self.session.client("kafka")
        resource_id = resource.get("id")

        try:
            client.delete_cluster(ClusterArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting KAFKA resource {resource_id}: {str(e)}")
            return False
