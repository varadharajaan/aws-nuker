"""Handler for MEDIALIVE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MedialiveHandler(ResourceHandler):
    """Handler for MEDIALIVE resources."""

    @property
    def service_name(self) -> str:
        return "medialive"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEDIALIVE resources."""
        client = self.session.client("medialive")
        resources = []

        try:
            paginator = client.get_paginator("list_channels")
            for page in paginator.paginate():
                for item in page.get("Channels", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "channel",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing MEDIALIVE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEDIALIVE resource."""
        client = self.session.client("medialive")
        resource_id = resource.get("id")

        try:
            client.delete_channel(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEDIALIVE resource {resource_id}: {str(e)}")
            return False
