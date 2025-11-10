"""Handler for CLOUDTRAIL resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudtrailHandler(ResourceHandler):
    """Handler for CLOUDTRAIL resources."""

    @property
    def service_name(self) -> str:
        return "cloudtrail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUDTRAIL resources."""
        client = self.session.client("cloudtrail")
        resources = []

        try:
            response = client.list_trails()
            for item in response.get("Trails", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "trail",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUDTRAIL resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUDTRAIL resource."""
        client = self.session.client("cloudtrail")
        resource_id = resource.get("id")

        try:
            client.delete_trail(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUDTRAIL resource {resource_id}: {str(e)}")
            return False
