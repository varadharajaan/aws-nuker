"""EMR (Elastic MapReduce) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EMRHandler(ResourceHandler):
    """Handler for EMR clusters."""

    @property
    def service_name(self) -> str:
        return "emr"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EMR clusters."""
        emr = self.session.client("emr")
        resources = []

        try:
            # List active and waiting clusters
            paginator = emr.get_paginator("list_clusters")
            for page in paginator.paginate(
                ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"]
            ):
                for cluster in page.get("Clusters", []):
                    resources.append({
                        "id": cluster["Id"],
                        "name": cluster.get("Name", cluster["Id"]),
                        "type": "cluster",
                        "status": cluster.get("Status", {}).get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing EMR clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Terminate an EMR cluster."""
        emr = self.session.client("emr")
        cluster_id = resource.get("id")

        try:
            emr.terminate_job_flows(JobFlowIds=[cluster_id])
            return True
        except ClientError as e:
            self.logger.error(
                f"Error terminating EMR cluster {cluster_id}: {str(e)}"
            )
            return False
