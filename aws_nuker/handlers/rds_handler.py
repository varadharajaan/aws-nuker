"""RDS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RDSHandler(ResourceHandler):
    """Handler for RDS databases and related resources."""

    @property
    def service_name(self) -> str:
        return "rds"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RDS instances and clusters."""
        rds = self.session.client("rds")
        resources = []

        try:
            # List DB instances
            instances_response = rds.describe_db_instances()
            for instance in instances_response.get("DBInstances", []):
                resources.append({
                    "id": instance["DBInstanceIdentifier"],
                    "name": instance["DBInstanceIdentifier"],
                    "type": "db_instance",
                    "engine": instance.get("Engine", ""),
                    "status": instance.get("DBInstanceStatus", ""),
                })

            # List DB clusters (Aurora)
            clusters_response = rds.describe_db_clusters()
            for cluster in clusters_response.get("DBClusters", []):
                resources.append({
                    "id": cluster["DBClusterIdentifier"],
                    "name": cluster["DBClusterIdentifier"],
                    "type": "db_cluster",
                    "engine": cluster.get("Engine", ""),
                    "status": cluster.get("Status", ""),
                })

            # List DB snapshots
            snapshots_response = rds.describe_db_snapshots()
            for snapshot in snapshots_response.get("DBSnapshots", []):
                if snapshot.get("SnapshotType") == "manual":
                    resources.append({
                        "id": snapshot["DBSnapshotIdentifier"],
                        "name": snapshot["DBSnapshotIdentifier"],
                        "type": "db_snapshot",
                        "status": snapshot.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing RDS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an RDS resource."""
        rds = self.session.client("rds")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "db_instance":
                # Delete DB instance without final snapshot
                rds.delete_db_instance(
                    DBInstanceIdentifier=resource_id,
                    SkipFinalSnapshot=True,
                    DeleteAutomatedBackups=True,
                )
                return True

            elif resource_type == "db_cluster":
                # Delete DB cluster without final snapshot
                rds.delete_db_cluster(
                    DBClusterIdentifier=resource_id,
                    SkipFinalSnapshot=True,
                )
                return True

            elif resource_type == "db_snapshot":
                # Delete DB snapshot
                rds.delete_db_snapshot(DBSnapshotIdentifier=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting RDS {resource_type} {resource_id}: {str(e)}"
            )
            return False
