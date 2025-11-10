"""Handler for MEDIAPACKAGE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediapackageHandler(ResourceHandler):
    """Handler for MEDIAPACKAGE resources."""

    @property
    def service_name(self) -> str:
        return "mediapackage"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEDIAPACKAGE resources."""
        client = self.session.client("mediapackage")
        resources = []

        try:
            response = client.list_channels()
            for item in response.get("Channels", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("Id", ""),
                    "type": "channel",
                })
        except ClientError as e:
            self.logger.error(f"Error listing MEDIAPACKAGE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEDIAPACKAGE resource."""
        client = self.session.client("mediapackage")
        resource_id = resource.get("id")

        try:
            client.delete_channel(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEDIAPACKAGE resource {resource_id}: {str(e)}")
            return False
