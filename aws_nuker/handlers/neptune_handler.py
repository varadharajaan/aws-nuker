"""Neptune resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class NeptuneHandler(ResourceHandler):
    """Handler for Neptune database clusters."""

    @property
    def service_name(self) -> str:
        return "neptune"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Neptune database clusters."""
        neptune = self.session.client("neptune")
        resources = []

        try:
            # List DB clusters
            paginator = neptune.get_paginator("describe_db_clusters")
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
            self.logger.error(f"Error listing Neptune clusters: {str(e)}")

        try:
            # List DB instances
            paginator = neptune.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                for instance in page.get("DBInstances", []):
                    # Only include Neptune instances
                    if instance.get("Engine", "").startswith("neptune"):
                        resources.append({
                            "id": instance["DBInstanceIdentifier"],
                            "name": instance["DBInstanceIdentifier"],
                            "type": "db_instance",
                            "engine": instance.get("Engine", ""),
                            "status": instance.get("DBInstanceStatus", ""),
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Neptune instances: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Neptune resource."""
        neptune = self.session.client("neptune")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "db_instance":
                neptune.delete_db_instance(
                    DBInstanceIdentifier=resource_id,
                    SkipFinalSnapshot=True
                )
                return True

            elif resource_type == "db_cluster":
                neptune.delete_db_cluster(
                    DBClusterIdentifier=resource_id,
                    SkipFinalSnapshot=True
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Neptune {resource_type} {resource_id}: {str(e)}"
            )
            return False
