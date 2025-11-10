"""Handler for RAM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RamHandler(ResourceHandler):
    """Handler for RAM resources."""

    @property
    def service_name(self) -> str:
        return "ram"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RAM resources."""
        client = self.session.client("ram")
        resources = []

        try:
            paginator = client.get_paginator("get_resource_shares")
            for page in paginator.paginate():
                for item in page.get("resourceShares", []):
                    resources.append({
                        "id": item.get("resourceShareArn", ""),
                        "name": item.get("name", ""),
                        "type": "share",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing RAM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a RAM resource."""
        client = self.session.client("ram")
        resource_id = resource.get("id")

        try:
            client.delete_resource_share(resourceShareArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting RAM resource {resource_id}: {str(e)}")
            return False
