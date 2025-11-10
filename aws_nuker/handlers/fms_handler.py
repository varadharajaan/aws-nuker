"""Handler for FMS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FmsHandler(ResourceHandler):
    """Handler for FMS resources."""

    @property
    def service_name(self) -> str:
        return "fms"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FMS resources."""
        client = self.session.client("fms")
        resources = []

        try:
            paginator = client.get_paginator("list_policies")
            for page in paginator.paginate():
                for item in page.get("PolicyList", []):
                    resources.append({
                        "id": item.get("PolicyId", ""),
                        "name": item.get("PolicyName", ""),
                        "type": "policy",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing FMS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a FMS resource."""
        client = self.session.client("fms")
        resource_id = resource.get("id")

        try:
            client.delete_policy(PolicyId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting FMS resource {resource_id}: {str(e)}")
            return False
