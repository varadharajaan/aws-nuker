"""Handler for IVS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IvsHandler(ResourceHandler):
    """Handler for IVS resources."""

    @property
    def service_name(self) -> str:
        return "ivs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IVS resources."""
        client = self.session.client("ivs")
        resources = []

        try:
            paginator = client.get_paginator("list_channels")
            for page in paginator.paginate():
                for item in page.get("channels", []):
                    resources.append({
                        "id": item.get("arn", ""),
                        "name": item.get("name", ""),
                        "type": "channel",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing IVS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IVS resource."""
        client = self.session.client("ivs")
        resource_id = resource.get("id")

        try:
            client.delete_channel(arn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IVS resource {resource_id}: {str(e)}")
            return False
