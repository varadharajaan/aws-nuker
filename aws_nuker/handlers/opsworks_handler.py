"""Handler for OPSWORKS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OpsworksHandler(ResourceHandler):
    """Handler for OPSWORKS resources."""

    @property
    def service_name(self) -> str:
        return "opsworks"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OPSWORKS resources."""
        client = self.session.client("opsworks")
        resources = []

        try:
            response = client.describe_stacks()
            for item in response.get("Stacks", []):
                resources.append({
                    "id": item.get("StackId", ""),
                    "name": item.get("Name", ""),
                    "type": "stack",
                })
        except ClientError as e:
            self.logger.error(f"Error listing OPSWORKS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a OPSWORKS resource."""
        client = self.session.client("opsworks")
        resource_id = resource.get("id")

        try:
            client.delete_stack(StackId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting OPSWORKS resource {resource_id}: {str(e)}")
            return False
