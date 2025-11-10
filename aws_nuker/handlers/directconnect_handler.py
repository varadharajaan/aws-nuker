"""Handler for DIRECTCONNECT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DirectconnectHandler(ResourceHandler):
    """Handler for DIRECTCONNECT resources."""

    @property
    def service_name(self) -> str:
        return "directconnect"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DIRECTCONNECT resources."""
        client = self.session.client("directconnect")
        resources = []

        try:
            response = client.describe_connections()
            for item in response.get("connections", []):
                resources.append({
                    "id": item.get("connectionId", ""),
                    "name": item.get("connectionName", ""),
                    "type": "connection",
                })
        except ClientError as e:
            self.logger.error(f"Error listing DIRECTCONNECT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DIRECTCONNECT resource."""
        client = self.session.client("directconnect")
        resource_id = resource.get("id")

        try:
            client.delete_connection(connectionId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DIRECTCONNECT resource {resource_id}: {str(e)}")
            return False
