"""Handler for AUTOSCALING resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AutoscalingHandler(ResourceHandler):
    """Handler for AUTOSCALING resources."""

    @property
    def service_name(self) -> str:
        return "autoscaling"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AUTOSCALING resources."""
        client = self.session.client("autoscaling")
        resources = []

        try:
            paginator = client.get_paginator("describe_auto_scaling_groups")
            for page in paginator.paginate():
                for item in page.get("AutoScalingGroups", []):
                    resources.append({
                        "id": item.get("AutoScalingGroupName", ""),
                        "name": item.get("AutoScalingGroupName", ""),
                        "type": "group",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing AUTOSCALING resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a AUTOSCALING resource."""
        client = self.session.client("autoscaling")
        resource_id = resource.get("id")

        try:
            client.delete_auto_scaling_group(AutoScalingGroupName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting AUTOSCALING resource {resource_id}: {str(e)}")
            return False
