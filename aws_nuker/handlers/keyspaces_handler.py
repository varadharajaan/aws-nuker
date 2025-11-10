"""Handler for KEYSPACES resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KeyspacesHandler(ResourceHandler):
    """Handler for KEYSPACES resources."""

    @property
    def service_name(self) -> str:
        return "keyspaces"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all KEYSPACES resources."""
        client = self.session.client("keyspaces")
        resources = []

        try:
            paginator = client.get_paginator("list_keyspaces")
            for page in paginator.paginate():
                for item in page.get("keyspaces", []):
                    resources.append({
                        "id": item.get("keyspaceName", ""),
                        "name": item.get("keyspaceName", ""),
                        "type": "keyspace",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing KEYSPACES resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a KEYSPACES resource."""
        client = self.session.client("keyspaces")
        resource_id = resource.get("id")

        try:
            client.delete_keyspace(keyspaceName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting KEYSPACES resource {resource_id}: {str(e)}")
            return False
