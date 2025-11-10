"""Handler for MEDIASTORE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediastoreHandler(ResourceHandler):
    """Handler for MEDIASTORE resources."""

    @property
    def service_name(self) -> str:
        return "mediastore"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEDIASTORE resources."""
        client = self.session.client("mediastore")
        resources = []

        try:
            paginator = client.get_paginator("list_containers")
            for page in paginator.paginate():
                for item in page.get("Containers", []):
                    resources.append({
                        "id": item.get("Name", ""),
                        "name": item.get("Name", ""),
                        "type": "container",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing MEDIASTORE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEDIASTORE resource."""
        client = self.session.client("mediastore")
        resource_id = resource.get("id")

        try:
            client.delete_container(ContainerName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEDIASTORE resource {resource_id}: {str(e)}")
            return False
