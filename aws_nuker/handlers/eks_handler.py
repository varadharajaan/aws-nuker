"""EKS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EKSHandler(ResourceHandler):
    """Handler for Elastic Kubernetes Service clusters."""

    @property
    def service_name(self) -> str:
        return "eks"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EKS clusters."""
        eks = self.session.client("eks")
        resources = []

        try:
            # List clusters
            cluster_response = eks.list_clusters()
            for cluster_name in cluster_response.get("clusters", []):
                resources.append({
                    "id": cluster_name,
                    "name": cluster_name,
                    "type": "cluster",
                })

        except ClientError as e:
            self.logger.error(f"Error listing EKS clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EKS cluster."""
        eks = self.session.client("eks")
        cluster_name = resource.get("name")

        try:
            # First, delete all node groups
            self._delete_nodegroups(eks, cluster_name)

            # Then delete the cluster
            eks.delete_cluster(name=cluster_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting EKS cluster {cluster_name}: {str(e)}"
            )
            return False

    def _delete_nodegroups(self, eks, cluster_name: str):
        """Delete all node groups in a cluster."""
        try:
            nodegroups = eks.list_nodegroups(clusterName=cluster_name)
            for ng_name in nodegroups.get("nodegroups", []):
                try:
                    eks.delete_nodegroup(
                        clusterName=cluster_name,
                        nodegroupName=ng_name
                    )
                except ClientError as e:
                    self.logger.warning(
                        f"Error deleting nodegroup {ng_name}: {str(e)}"
                    )
        except ClientError as e:
            self.logger.warning(
                f"Error listing nodegroups for {cluster_name}: {str(e)}"
            )
