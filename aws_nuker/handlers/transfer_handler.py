"""Handler for TRANSFER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TransferHandler(ResourceHandler):
    """Handler for AWS Transfer Family resources."""

    @property
    def service_name(self) -> str:
        return "transfer"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Transfer Family servers."""
        client = self.session.client("transfer")
        resources = []

        try:
            paginator = client.get_paginator("list_servers")
            for page in paginator.paginate():
                for item in page.get("Servers", []):
                    resources.append({
                        "id": item.get("ServerId", ""),
                        "name": item.get("ServerId", ""),
                        "type": "server",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing TRANSFER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Transfer Family server."""
        client = self.session.client("transfer")
        resource_id = resource.get("id")

        try:
            client.delete_server(ServerId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting TRANSFER resource {resource_id}: {str(e)}")
            return False
