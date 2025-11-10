"""Handler for QLDB resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class QldbHandler(ResourceHandler):
    """Handler for QLDB resources."""

    @property
    def service_name(self) -> str:
        return "qldb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all QLDB resources."""
        client = self.session.client("qldb")
        resources = []

        try:
            response = client.list_ledgers()
            for item in response.get("Ledgers", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "ledger",
                })
        except ClientError as e:
            self.logger.error(f"Error listing QLDB resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a QLDB resource."""
        client = self.session.client("qldb")
        resource_id = resource.get("id")

        try:
            client.delete_ledger(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting QLDB resource {resource_id}: {str(e)}")
            return False
