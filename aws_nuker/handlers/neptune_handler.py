"""Handler for NEPTUNE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class NeptuneHandler(ResourceHandler):
    """Handler for NEPTUNE resources."""

    @property
    def service_name(self) -> str:
        return "neptune"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all NEPTUNE resources."""
        client = self.session.client("neptune")
        resources = []

        try:
            paginator = client.get_paginator("describe_db_clusters")
            for page in paginator.paginate():
                for item in page.get("DBClusters", []):
                    resources.append({
                        "id": item.get("DBClusterIdentifier", ""),
                        "name": item.get("DBClusterIdentifier", ""),
                        "type": "cluster",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing NEPTUNE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a NEPTUNE resource."""
        client = self.session.client("neptune")
        resource_id = resource.get("id")

        try:
            client.delete_db_cluster(DBClusterIdentifier=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting NEPTUNE resource {resource_id}: {str(e)}")
            return False
