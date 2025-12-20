"""MediaStore resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaStoreHandler(ResourceHandler):
    """Handler for AWS Elemental MediaStore resources."""

    @property
    def service_name(self) -> str:
        return "mediastore"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MediaStore containers."""
        mediastore = self.session.client("mediastore")
        resources = []

        try:
            # List containers
            paginator = mediastore.get_paginator("list_containers")
            for page in paginator.paginate():
                for container in page.get("Containers", []):
                    resources.append({
                        "id": container["ARN"],
                        "name": container["Name"],
                        "type": "container",
                        "status": container.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaStore containers: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MediaStore container."""
        mediastore = self.session.client("mediastore")
        container_name = resource.get("name")

        try:
            mediastore.delete_container(ContainerName=container_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting MediaStore container {container_name}: {str(e)}"
            )
            return False
