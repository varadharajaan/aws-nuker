"""MSK (Managed Streaming for Apache Kafka) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KafkaHandler(ResourceHandler):
    """Handler for MSK (Kafka) clusters."""

    @property
    def service_name(self) -> str:
        return "kafka"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MSK clusters."""
        kafka = self.session.client("kafka")
        resources = []

        try:
            # List clusters
            paginator = kafka.get_paginator("list_clusters")
            for page in paginator.paginate():
                for cluster in page.get("ClusterInfoList", []):
                    resources.append({
                        "id": cluster["ClusterArn"],
                        "name": cluster["ClusterName"],
                        "type": "cluster",
                        "state": cluster.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MSK clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an MSK cluster."""
        kafka = self.session.client("kafka")
        cluster_arn = resource.get("id")

        try:
            kafka.delete_cluster(ClusterArn=cluster_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting MSK cluster {cluster_arn}: {str(e)}"
            )
            return False
