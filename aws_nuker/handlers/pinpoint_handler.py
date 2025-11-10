"""Handler for PINPOINT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PinpointHandler(ResourceHandler):
    """Handler for PINPOINT resources."""

    @property
    def service_name(self) -> str:
        return "pinpoint"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all PINPOINT resources."""
        client = self.session.client("pinpoint")
        resources = []

        try:
            response = client.get_apps()
            for item in response.get("ApplicationsResponse", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("Name", ""),
                    "type": "app",
                })
        except ClientError as e:
            self.logger.error(f"Error listing PINPOINT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a PINPOINT resource."""
        client = self.session.client("pinpoint")
        resource_id = resource.get("id")

        try:
            client.delete_app(ApplicationId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting PINPOINT resource {resource_id}: {str(e)}")
            return False
