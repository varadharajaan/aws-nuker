"""Handler for MEDIATAILOR resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediatailorHandler(ResourceHandler):
    """Handler for MEDIATAILOR resources."""

    @property
    def service_name(self) -> str:
        return "mediatailor"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEDIATAILOR resources."""
        client = self.session.client("mediatailor")
        resources = []

        try:
            response = client.list_playback_configurations()
            for item in response.get("Items", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "config",
                })
        except ClientError as e:
            self.logger.error(f"Error listing MEDIATAILOR resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEDIATAILOR resource."""
        client = self.session.client("mediatailor")
        resource_id = resource.get("id")

        try:
            client.delete_playback_configuration(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEDIATAILOR resource {resource_id}: {str(e)}")
            return False
