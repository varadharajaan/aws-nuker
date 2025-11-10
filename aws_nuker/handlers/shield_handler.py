"""Handler for SHIELD resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ShieldHandler(ResourceHandler):
    """Handler for SHIELD resources."""

    @property
    def service_name(self) -> str:
        return "shield"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SHIELD resources."""
        client = self.session.client("shield")
        resources = []

        try:
            response = client.list_protections()
            for item in response.get("Protections", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("Name", ""),
                    "type": "protection",
                })
        except ClientError as e:
            self.logger.error(f"Error listing SHIELD resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SHIELD resource."""
        client = self.session.client("shield")
        resource_id = resource.get("id")

        try:
            client.delete_protection(ProtectionId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SHIELD resource {resource_id}: {str(e)}")
            return False
