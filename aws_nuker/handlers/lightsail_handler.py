"""Handler for LIGHTSAIL resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LightsailHandler(ResourceHandler):
    """Handler for LIGHTSAIL resources."""

    @property
    def service_name(self) -> str:
        return "lightsail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all LIGHTSAIL resources."""
        client = self.session.client("lightsail")
        resources = []

        try:
            response = client.get_instances()
            for item in response.get("instances", []):
                resources.append({
                    "id": item.get("name", ""),
                    "name": item.get("name", ""),
                    "type": "instance",
                })
        except ClientError as e:
            self.logger.error(f"Error listing LIGHTSAIL resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a LIGHTSAIL resource."""
        client = self.session.client("lightsail")
        resource_id = resource.get("id")

        try:
            client.delete_instance(instanceName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting LIGHTSAIL resource {resource_id}: {str(e)}")
            return False
