"""MediaPackage resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaPackageHandler(ResourceHandler):
    """Handler for AWS Elemental MediaPackage resources."""

    @property
    def service_name(self) -> str:
        return "mediapackage"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MediaPackage resources."""
        mediapackage = self.session.client("mediapackage")
        resources = []

        try:
            # List channels
            paginator = mediapackage.get_paginator("list_channels")
            for page in paginator.paginate():
                for channel in page.get("Channels", []):
                    resources.append({
                        "id": channel["Id"],
                        "name": channel.get("Description", channel["Id"]),
                        "type": "channel",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaPackage channels: {str(e)}")

        try:
            # List origin endpoints
            paginator = mediapackage.get_paginator("list_origin_endpoints")
            for page in paginator.paginate():
                for endpoint in page.get("OriginEndpoints", []):
                    resources.append({
                        "id": endpoint["Id"],
                        "name": endpoint.get("Description", endpoint["Id"]),
                        "type": "origin_endpoint",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaPackage origin endpoints: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MediaPackage resource."""
        mediapackage = self.session.client("mediapackage")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "origin_endpoint":
                mediapackage.delete_origin_endpoint(Id=resource_id)
                return True

            elif resource_type == "channel":
                mediapackage.delete_channel(Id=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting MediaPackage {resource_type} {resource_id}: {str(e)}"
            )
            return False
