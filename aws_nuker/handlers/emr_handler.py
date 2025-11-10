"""Handler for EMR resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EmrHandler(ResourceHandler):
    """Handler for EMR resources."""

    @property
    def service_name(self) -> str:
        return "emr"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EMR resources."""
        client = self.session.client("emr")
        resources = []

        try:
            paginator = client.get_paginator("list_clusters")
            for page in paginator.paginate():
                for item in page.get("Clusters", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "cluster",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing EMR resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a EMR resource."""
        client = self.session.client("emr")
        resource_id = resource.get("id")

        try:
            client.terminate_job_flows(JobFlowIds=[resource_id])
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting EMR resource {resource_id}: {str(e)}")
            return False
