"""Handler for CHIME resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ChimeHandler(ResourceHandler):
    """Handler for CHIME resources."""

    @property
    def service_name(self) -> str:
        return "chime"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CHIME resources."""
        client = self.session.client("chime")
        resources = []

        try:
            response = client.list_accounts()
            for item in response.get("Accounts", []):
                resources.append({
                    "id": item.get("AccountId", ""),
                    "name": item.get("Name", ""),
                    "type": "account",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CHIME resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CHIME resource."""
        client = self.session.client("chime")
        resource_id = resource.get("id")

        try:
            client.delete_account(AccountId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CHIME resource {resource_id}: {str(e)}")
            return False
