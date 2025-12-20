"""ECS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ECSHandler(ResourceHandler):
    """Handler for ECS clusters, services, and tasks."""

    @property
    def service_name(self) -> str:
        return "ecs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ECS resources."""
        ecs = self.session.client("ecs")
        resources = []

        try:
            # List clusters
            clusters_response = ecs.list_clusters()
            for cluster_arn in clusters_response.get("clusterArns", []):
                cluster_name = cluster_arn.split("/")[-1]
                resources.append({
                    "id": cluster_arn,
                    "name": cluster_name,
                    "type": "cluster",
                })

                # List services in cluster
                services_response = ecs.list_services(cluster=cluster_arn)
                for service_arn in services_response.get("serviceArns", []):
                    service_name = service_arn.split("/")[-1]
                    resources.append({
                        "id": service_arn,
                        "name": service_name,
                        "type": "service",
                        "cluster": cluster_arn,
                    })

        except ClientError as e:
            self.logger.error(f"Error listing ECS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ECS resource."""
        ecs = self.session.client("ecs")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "service":
                # Delete service
                cluster = resource.get("cluster")
                ecs.delete_service(
                    cluster=cluster,
                    service=resource_id,
                    force=self.force,
                )
                return True

            elif resource_type == "cluster":
                # Delete cluster
                ecs.delete_cluster(cluster=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting ECS {resource_type} {resource_id}: {str(e)}"
            )
            return False
