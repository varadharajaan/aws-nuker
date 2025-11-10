"""Handler for CONFIG resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ConfigHandler(ResourceHandler):
    """Handler for CONFIG resources."""

    @property
    def service_name(self) -> str:
        return "config"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CONFIG resources."""
        client = self.session.client("config")
        resources = []

        try:
            response = client.describe_configuration_recorders()
            for item in response.get("ConfigurationRecorders", []):
                resources.append({
                    "id": item.get("name", ""),
                    "name": item.get("name", ""),
                    "type": "recorder",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CONFIG resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CONFIG resource."""
        client = self.session.client("config")
        resource_id = resource.get("id")

        try:
            client.delete_configuration_recorder(ConfigurationRecorderName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CONFIG resource {resource_id}: {str(e)}")
            return False
