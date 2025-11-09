"""Redshift resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RedshiftHandler(ResourceHandler):
    """Handler for Amazon Redshift clusters."""

    @property
    def service_name(self) -> str:
        return "redshift"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Redshift clusters."""
        redshift = self.session.client("redshift")
        resources = []

        try:
            # List clusters
            clusters_response = redshift.describe_clusters()
            for cluster in clusters_response.get("Clusters", []):
                resources.append({
                    "id": cluster["ClusterIdentifier"],
                    "name": cluster["ClusterIdentifier"],
                    "type": "cluster",
                    "status": cluster.get("ClusterStatus", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Redshift clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Redshift cluster."""
        redshift = self.session.client("redshift")
        cluster_id = resource.get("id")

        try:
            # Delete cluster without final snapshot
            redshift.delete_cluster(
                ClusterIdentifier=cluster_id,
                SkipFinalClusterSnapshot=True
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Redshift cluster {cluster_id}: {str(e)}"
            )
            return False
