"""DocumentDB resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DocumentDBHandler(ResourceHandler):
    """Handler for DocumentDB database clusters."""

    @property
    def service_name(self) -> str:
        return "docdb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DocumentDB database clusters."""
        docdb = self.session.client("docdb")
        resources = []

        try:
            # List DB clusters
            paginator = docdb.get_paginator("describe_db_clusters")
            for page in paginator.paginate():
                for cluster in page.get("DBClusters", []):
                    resources.append({
                        "id": cluster["DBClusterIdentifier"],
                        "name": cluster["DBClusterIdentifier"],
                        "type": "db_cluster",
                        "engine": cluster.get("Engine", ""),
                        "status": cluster.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DocumentDB clusters: {str(e)}")

        try:
            # List DB instances
            paginator = docdb.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                for instance in page.get("DBInstances", []):
                    # Only include DocumentDB instances
                    if instance.get("Engine", "").startswith("docdb"):
                        resources.append({
                            "id": instance["DBInstanceIdentifier"],
                            "name": instance["DBInstanceIdentifier"],
                            "type": "db_instance",
                            "engine": instance.get("Engine", ""),
                            "status": instance.get("DBInstanceStatus", ""),
                        })

        except ClientError as e:
            self.logger.error(f"Error listing DocumentDB instances: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DocumentDB resource."""
        docdb = self.session.client("docdb")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "db_instance":
                docdb.delete_db_instance(DBInstanceIdentifier=resource_id)
                return True

            elif resource_type == "db_cluster":
                docdb.delete_db_cluster(
                    DBClusterIdentifier=resource_id,
                    SkipFinalSnapshot=True
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting DocumentDB {resource_type} {resource_id}: {str(e)}"
            )
            return False
