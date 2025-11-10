"""Handler for APPSTREAM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppstreamHandler(ResourceHandler):
    """Handler for APPSTREAM resources."""

    @property
    def service_name(self) -> str:
        return "appstream"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all APPSTREAM resources."""
        client = self.session.client("appstream")
        resources = []

        try:
            response = client.describe_fleets()
            for item in response.get("Fleets", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "fleet",
                })
        except ClientError as e:
            self.logger.error(f"Error listing APPSTREAM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a APPSTREAM resource."""
        client = self.session.client("appstream")
        resource_id = resource.get("id")

        try:
            client.delete_fleet(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting APPSTREAM resource {resource_id}: {str(e)}")
            return False
