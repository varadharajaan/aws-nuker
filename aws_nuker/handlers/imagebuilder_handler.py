"""Handler for IMAGEBUILDER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ImagebuilderHandler(ResourceHandler):
    """Handler for IMAGEBUILDER resources."""

    @property
    def service_name(self) -> str:
        return "imagebuilder"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IMAGEBUILDER resources."""
        client = self.session.client("imagebuilder")
        resources = []

        try:
            response = client.list_images()
            for item in response.get("imageVersionList", []):
                resources.append({
                    "id": item.get("arn", ""),
                    "name": item.get("arn", ""),
                    "type": "image",
                })
        except ClientError as e:
            self.logger.error(f"Error listing IMAGEBUILDER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IMAGEBUILDER resource."""
        client = self.session.client("imagebuilder")
        resource_id = resource.get("id")

        try:
            client.delete_image(imageBuildVersionArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IMAGEBUILDER resource {resource_id}: {str(e)}")
            return False
