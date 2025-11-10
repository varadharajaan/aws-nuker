"""Handler for DOCDB resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DocdbHandler(ResourceHandler):
    """Handler for DOCDB resources."""

    @property
    def service_name(self) -> str:
        return "docdb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DOCDB resources."""
        client = self.session.client("docdb")
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
            self.logger.error(f"Error listing DOCDB resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DOCDB resource."""
        client = self.session.client("docdb")
        resource_id = resource.get("id")

        try:
            client.delete_db_cluster(DBClusterIdentifier=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DOCDB resource {resource_id}: {str(e)}")
            return False
