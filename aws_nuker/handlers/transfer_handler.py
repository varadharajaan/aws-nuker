"""Transfer Family resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TransferHandler(ResourceHandler):
    """Handler for Transfer Family servers."""

    @property
    def service_name(self) -> str:
        return "transfer"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Transfer Family servers."""
        transfer = self.session.client("transfer")
        resources = []

        try:
            # List servers
            paginator = transfer.get_paginator("list_servers")
            for page in paginator.paginate():
                for server in page.get("Servers", []):
                    resources.append({
                        "id": server["ServerId"],
                        "name": server["ServerId"],
                        "type": "server",
                        "state": server.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Transfer Family servers: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Transfer Family server."""
        transfer = self.session.client("transfer")
        server_id = resource.get("id")

        try:
            transfer.delete_server(ServerId=server_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Transfer Family server {server_id}: {str(e)}"
            )
            return False
