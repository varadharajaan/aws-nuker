"""CloudHSM resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudHSMHandler(ResourceHandler):
    """Handler for AWS CloudHSM resources."""

    @property
    def service_name(self) -> str:
        return "cloudhsm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudHSM clusters."""
        cloudhsmv2 = self.session.client("cloudhsmv2")
        resources = []

        try:
            # List clusters
            paginator = cloudhsmv2.get_paginator("describe_clusters")
            for page in paginator.paginate():
                for cluster in page.get("Clusters", []):
                    resources.append({
                        "id": cluster["ClusterId"],
                        "name": cluster.get("ClusterId"),
                        "type": "cluster",
                        "state": cluster.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CloudHSM clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudHSM cluster."""
        cloudhsmv2 = self.session.client("cloudhsmv2")
        cluster_id = resource.get("id")

        try:
            cloudhsmv2.delete_cluster(ClusterId=cluster_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudHSM cluster {cluster_id}: {str(e)}"
            )
            return False
