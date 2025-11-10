"""Handler for REKOGNITION resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RekognitionHandler(ResourceHandler):
    """Handler for REKOGNITION resources."""

    @property
    def service_name(self) -> str:
        return "rekognition"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all REKOGNITION resources."""
        client = self.session.client("rekognition")
        resources = []

        try:
            response = client.list_collections()
            for collection_id in response.get("CollectionIds", []):
                resources.append({
                    "id": collection_id,
                    "name": collection_id,
                    "type": "collection",
                })
        except ClientError as e:
            self.logger.error(f"Error listing REKOGNITION resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a REKOGNITION resource."""
        client = self.session.client("rekognition")
        resource_id = resource.get("id")

        try:
            client.delete_collection(CollectionId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting REKOGNITION resource {resource_id}: {str(e)}")
            return False
